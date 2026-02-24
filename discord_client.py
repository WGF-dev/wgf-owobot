"""
Discord API ile kanala mesaj gönderme.
Rate limit header'larına göre 429 durumunda bekler.
"""
import logging

import requests

logger = logging.getLogger(__name__)

DISCORD_API = "https://discord.com/api/v10"


def send_message(token: str, channel_id: str, content: str) -> tuple[bool, str | None, dict]:
    """
    Kanala mesaj gönder.
    Returns: (success, error_message_or_none, response_info)
    response_info: {"status_code", "retry_after", "json"} vb.
    """
    url = f"{DISCORD_API}/channels/{channel_id}/messages"
    headers = {
        "Authorization": token.strip(),
        "Content-Type": "application/json",
    }
    payload = {"content": content}

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        logger.error("İstek hatası: %s", e)
        return False, str(e), {}

    info = {"status_code": r.status_code}

    if r.status_code == 200:
        try:
            info["json"] = r.json()
        except Exception:
            pass
        return True, None, info

    if r.status_code == 429:
        # Rate limit: Retry-After (saniye) veya retry_after (ms) kullan
        retry_after = r.headers.get("Retry-After")
        if retry_after:
            try:
                info["retry_after"] = float(retry_after)
            except ValueError:
                info["retry_after"] = 60.0
        else:
            try:
                data = r.json()
                info["retry_after"] = data.get("retry_after", 60) / 1000.0
            except Exception:
                info["retry_after"] = 60.0
        return False, "rate_limit", info

    try:
        data = r.json()
        msg = data.get("message", r.text)
    except Exception:
        msg = r.text or str(r.status_code)
    logger.warning("Discord API %s: %s", r.status_code, msg)
    return False, msg, info


def is_likely_captcha_response(text: str) -> bool:
    """
    OwO bot yanıtında captcha/doğrulama ifadesi var mı kontrol et.
    """
    if not text:
        return False
    t = text.lower()
    captcha_keywords = (
        "captcha",
        "doğrula",
        "verify",
        "robot değil",
        "human",
        "click",
        "tıkla",
        "confirm",
    )
    return any(k in t for k in captcha_keywords)


def get_channel_messages(token: str, channel_id: str, limit: int = 5) -> tuple[bool, list, str]:
    """
    Kanalda son mesajları getir (OwO yanıtı / captcha kontrolü için).
    Returns: (success, list of message dicts, error_message)
    """
    url = f"{DISCORD_API}/channels/{channel_id}/messages"
    headers = {"Authorization": token.strip()}
    try:
        r = requests.get(url, headers=headers, params={"limit": limit}, timeout=15)
    except requests.RequestException as e:
        return False, [], str(e)
    if r.status_code != 200:
        return False, [], f"HTTP {r.status_code}"
    try:
        return True, r.json(), ""
    except Exception as e:
        return False, [], str(e)
