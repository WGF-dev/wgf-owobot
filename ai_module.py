"""
Yapay zeka katmanı: OwO bot yanıtlarını analiz eder (captcha, rate limit, başarı, hata).
OpenAI uyumlu API kullanır: OpenAI, Together, Ollama (yerel), vb.
"""
import json
import logging
import re

logger = logging.getLogger(__name__)

# OpenAI uyumlu istemci (opsiyonel; ai_enabled=True ve api_key doluysa kullanılır)
_openai_client = None


def _get_client(api_key: str, base_url: str | None):
    """OpenAI uyumlu istemci oluştur veya önbelleğe al."""
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    if not api_key or not api_key.strip():
        return None
    try:
        from openai import OpenAI
        kwargs = {"api_key": api_key.strip()}
        if base_url and base_url.strip():
            kwargs["base_url"] = base_url.strip().rstrip("/")
            if not kwargs["base_url"].endswith("/v1"):
                kwargs["base_url"] = kwargs["base_url"] + "/v1"
        _openai_client = OpenAI(**kwargs)
        logger.info("Yapay zeka bağlantısı hazır (model kullanılacak: config.ai_model)")
        return _openai_client
    except ImportError:
        logger.warning("openai paketi yok. pip install openai ile kurup AI kullanabilirsin.")
        return None
    except Exception as e:
        logger.warning("OpenAI istemci oluşturulamadı: %s", e)
        return None


def _messages_to_text(messages: list) -> str:
    """Discord mesaj listesini tek metin özetine çevir (son 5 mesaj)."""
    lines = []
    for i, msg in enumerate(messages[:5]):
        author = (msg.get("author") or {}).get("username", "?")
        content = msg.get("content") or ""
        for emb in msg.get("embeds", []):
            if emb.get("title"):
                content += " [Embed: " + emb["title"] + "]"
            if emb.get("description"):
                content += " " + emb["description"]
        lines.append(f"[{author}]: {content[:500]}")
    return "\n".join(lines)


SYSTEM_PROMPT = """Sen bir Discord OwO botu kanalındaki son mesajları analiz eden asistanısın.
Verilen mesaj metnini inceleyip ŞU FORMATTA sadece tek bir JSON satırı döndür (başka metin yazma):
{"status":"ok"|"captcha"|"rate_limit"|"error","reason":"kısa açıklama","wait_seconds":0}

Kurallar:
- status: "ok" = komut başarılı, normal devam et. "captcha" = kullanıcıdan captcha/doğrulama isteniyor (verify, click, human, robot değil, tıkla vb.). "rate_limit" = çok fazla istek veya bekleme süresi söyleniyor. "error" = başka hata veya anlaşılamayan durum.
- reason: Türkçe veya İngilizce kısa sebep.
- wait_seconds: captcha/rate_limit/error durumunda kaç saniye beklenmeli (0-120 arası), "ok" ise 0.

Sadece bu JSON satırını döndür, başka açıklama ekleme."""


def analyze_messages_with_ai(
    messages: list,
    api_key: str,
    model: str = "gpt-4o-mini",
    base_url: str | None = None,
) -> dict | None:
    """
    Son kanal mesajlarını LLM ile analiz et.
    Returns: {"status": "ok"|"captcha"|"rate_limit"|"error", "reason": "...", "wait_seconds": int}
    veya None (AI kullanılamadıysa).
    """
    client = _get_client(api_key, base_url)
    if not client:
        return None
    text = _messages_to_text(messages)
    if not text.strip():
        return {"status": "ok", "reason": "mesaj yok", "wait_seconds": 0}
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Son mesajlar:\n{text}"},
            ],
            max_tokens=200,
            temperature=0.1,
        )
        content = (resp.choices[0].message.content or "").strip()
        # JSON'u bul (tek satırda veya ```json ... ``` içinde)
        for part in (content, re.sub(r"```\w*\s*", "", content)):
            try:
                # İlk { ile son } arasını al (iç içe geçmiş olabilir)
                start = part.find("{")
                if start == -1:
                    continue
                depth = 0
                end = start
                for i, c in enumerate(part[start:], start):
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                if depth == 0:
                    data = json.loads(part[start : end + 1])
                    break
            except (json.JSONDecodeError, ValueError):
                continue
        else:
            return None
        status = (data.get("status") or "ok").lower()
        if status not in ("ok", "captcha", "rate_limit", "error"):
            status = "ok"
        return {
            "status": status,
            "reason": data.get("reason", ""),
            "wait_seconds": min(120, max(0, int(data.get("wait_seconds", 0)))),
        }
    except json.JSONDecodeError as e:
        logger.debug("AI yanıtı JSON parse edilemedi: %s", e)
        return None
    except Exception as e:
        logger.warning("AI analizi hatası: %s", e)
        return None
