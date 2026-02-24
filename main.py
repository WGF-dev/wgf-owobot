"""
OwO Bot Hunter - Tüm aktiviteler: hunt, kutu açma, silah kutusu, savaş, pet takımı.
config.py içinde token ve channel_id'yi doldur, ardından: python main.py
"""
import logging
import sys
import time

import config
from discord_client import (
    get_channel_messages,
    is_likely_captcha_response,
    send_message,
)
from rate_limit import get_delay, sleep_with_log
from tasks import Scheduler

# Logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def check_captcha_in_messages(token: str, channel_id: str) -> bool:
    """Son mesajlarda captcha var mı kontrol et."""
    ok, messages, err = get_channel_messages(token, channel_id, limit=5)
    if not ok:
        return False
    for msg in messages:
        content = (msg.get("content") or "") + " ".join(
            e.get("title", "") for e in msg.get("embeds", [])
        )
        if is_likely_captcha_response(content):
            return True
    return False


def analyze_response(token: str, channel_id: str) -> tuple[str, str, int]:
    """
    Kanal mesajlarını analiz et: AI açıksa LLM kullan, değilse sadece keyword captcha.
    Returns: (status, reason, wait_seconds) - status: "ok"|"captcha"|"rate_limit"|"error"
    """
    ok, messages, err = get_channel_messages(token, channel_id, limit=5)
    if not ok or not messages:
        return "ok", "", 0

    # Yapay zeka açıksa LLM ile analiz
    if getattr(config, "ai_enabled", False) and getattr(config, "ai_api_key", ""):
        from ai_module import analyze_messages_with_ai
        logger.info("Yapay zeka mesajları analiz ediyor...")
        result = analyze_messages_with_ai(
            messages,
            api_key=config.ai_api_key,
            model=getattr(config, "ai_model", "gpt-4o-mini"),
            base_url=getattr(config, "ai_base_url", None) or None,
        )
        if result:
            logger.info(
                "Yapay zeka sonucu: status=%s, reason=%s, bekleme=%ss",
                result.get("status", "ok"),
                result.get("reason", "") or "-",
                result.get("wait_seconds", 0),
            )
            return (
                result.get("status", "ok"),
                result.get("reason", ""),
                result.get("wait_seconds", 0),
            )
        logger.warning("Yapay zeka yanıt alamadı, anahtar kelime kontrolü kullanılıyor.")

    # Fallback: keyword ile captcha kontrolü
    for msg in messages:
        content = (msg.get("content") or "") + " ".join(
            e.get("title", "") for e in msg.get("embeds", [])
        )
        if is_likely_captcha_response(content):
            return "captcha", "Anahtar kelime tespiti", 60
    return "ok", "", 0


def run_hunter():
    if not config.token or not config.channel_id:
        logger.error("config.py içinde token ve channel_id doldurman gerekiyor.")
        sys.exit(1)

    scheduler = Scheduler(config)
    if not scheduler.activities:
        logger.error("Hiç aktivite açık değil. config.py içinde en az birini enabled=True yap.")
        sys.exit(1)

    base = config.base_delay_seconds
    randomize = config.randomize_delay
    min_j = config.min_random_delay_seconds
    max_j = config.max_random_delay_seconds
    max_cap = config.max_delay_seconds
    backoff = config.rate_limit_backoff_multiplier

    success_count = 0
    fail_count = 0
    consecutive_failures = 0

    logger.info(
        "OwO Hunter başlatıldı. Kanal: %s | Aktiviteler: %s",
        config.channel_id,
        [a[0] for a in scheduler.activities],
    )
    if getattr(config, "ai_enabled", False) and getattr(config, "ai_api_key", ""):
        logger.info("Yapay zeka analizi açık (model: %s)", getattr(config, "ai_model", "gpt-4o-mini"))
    logger.info("Rate limit: base=%ss, jitter=%s (%s-%ss)", base, randomize, min_j, max_j)

    while True:
        if config.max_consecutive_failures and consecutive_failures >= config.max_consecutive_failures:
            logger.warning(
                "Ardışık %s hata, durduruluyor.",
                config.max_consecutive_failures,
            )
            break

        name, cmd, wait_seconds = scheduler.next()
        if name is None:
            logger.warning("Scheduler aktivite döndürmedi, 60s bekleniyor.")
            sleep_with_log(60, "Bekleme")
            continue

        if wait_seconds > 0:
            sleep_with_log(min(wait_seconds, max_cap), f"[{name}] Süre dolması bekleniyor")

        ok, err, info = send_message(config.token, config.channel_id, cmd)

        if ok:
            success_count += 1
            consecutive_failures = 0
            scheduler.mark_done(name)
            logger.info("[%s] Gönderildi (#%s): %s", name, success_count, cmd[:40])
        else:
            fail_count += 1
            consecutive_failures += 1

            if err == "rate_limit":
                retry = info.get("retry_after", base * backoff)
                retry = min(retry, config.max_delay_seconds)
                logger.warning("Rate limit (429). %s saniye bekleniyor.", round(retry, 1))
                sleep_with_log(retry, "Rate limit beklemesi")
                continue
            else:
                logger.warning("[%s] Gönderilemedi: %s", name, err)

        # Yanıt analizi: captcha / rate_limit / hata (AI veya keyword)
        if getattr(config, "check_captcha_after_send", True):
            try:
                time.sleep(3)
                status, reason, wait_sec = analyze_response(config.token, config.channel_id)
                if status == "captcha":
                    logger.warning("Captcha / doğrulama tespit edildi. %s", reason or "")
                    if config.exit_on_captcha:
                        logger.info("Çıkılıyor (exit_on_captcha=True).")
                        break
                    sleep_with_log(wait_sec or 60, "Captcha sonrası bekleme")
                    continue
                if status == "rate_limit":
                    logger.warning("Rate limit benzeri yanıt. %s saniye bekleniyor. %s", wait_sec, reason or "")
                    sleep_with_log(min(wait_sec or 60, config.max_delay_seconds), "Ek bekleme")
                    continue
                if status == "error" and wait_sec > 0:
                    logger.warning("Hata tespit edildi: %s. %s saniye bekleniyor.", reason or "?", wait_sec)
                    sleep_with_log(min(wait_sec, config.max_delay_seconds), "Hata sonrası bekleme")
                    continue
            except Exception as e:
                logger.debug("Yanıt analizi atlandı: %s", e)

        # Komutlar arası minimum bekleme (rate limit)
        delay = get_delay(base, randomize, min_j, max_j, max_cap)
        sleep_with_log(delay, "Sonraki komut")

    logger.info("Bitti. Başarılı: %s, Başarısız: %s", success_count, fail_count)


if __name__ == "__main__":
    run_hunter()
