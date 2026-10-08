import time
from collections import defaultdict
from typing import Optional

from app.core.config import settings

_mem: dict = defaultdict(list)
_redis = None
_redis_failed_at = 0.0


def _get_redis() -> Optional[object]:
    global _redis, _redis_failed_at
    if _redis is not None:
        return _redis
    if time.time() - _redis_failed_at < 30:
        return None
    try:
        import redis
        r = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=0.3, socket_timeout=0.3)
        r.ping()
        _redis = r
    except Exception:
        _redis_failed_at = time.time()
    return _redis


def allow(key: str) -> bool:
    """Sliding-ish window per menit. Pakai Redis bila ada, fallback ke memori proses."""
    limit = settings.rate_limit_per_minute
    r = _get_redis()
    if r is not None:
        try:
            k = f"rl:{key}:{int(time.time() // 60)}"
            n = r.incr(k)
            if n == 1:
                r.expire(k, 70)
            return n <= limit
        except Exception:
            pass
    now = time.time()
    q = [t for t in _mem[key] if now - t < 60]
    q.append(now)
    _mem[key] = q
    return len(q) <= limit
