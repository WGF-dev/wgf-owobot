"""
Rate limit uyumlu bekleme ve jitter.
Discord ve OwO bot limitlerine uygun aralıklar üretir.
"""
import random
import time
import logging

logger = logging.getLogger(__name__)


def get_delay(
    base_seconds: float,
    randomize: bool = True,
    min_jitter: float = 1,
    max_jitter: float = 5,
    max_cap: float = 120,
) -> float:
    """
    Bir sonraki komut için bekleme süresi (saniye) hesapla.
    """
    delay = base_seconds
    if randomize and min_jitter < max_jitter:
        jitter = random.uniform(min_jitter, max_jitter)
        delay = base_seconds + jitter
    return min(max(delay, 1), max_cap)


def apply_rate_limit_backoff(
    base_delay: float,
    multiplier: float = 1.5,
    max_delay: float = 120,
) -> float:
    """
    429 rate limit sonrası kullanılacak ek bekleme süresi.
    """
    return min(base_delay * multiplier, max_delay)


def sleep_with_log(seconds: float, reason: str = "Bekleniyor"):
    """Log ile birlikte uyku."""
    logger.info("%s: %.1f saniye", reason, seconds)
    time.sleep(seconds)
