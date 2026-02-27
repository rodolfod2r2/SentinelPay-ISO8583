"""Velocity Check (antifraude) via Redis."""
import hashlib
import json
from typing import Callable, Awaitable

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


class RedisVelocityService:
    """Conta transações por PAN (hash) em uma janela; bloqueia se exceder limite."""

    def __init__(self, redis_url: str, window_seconds: int = 300, max_transactions: int = 10):
        self.redis_url = redis_url
        self.window_seconds = window_seconds
        self.max_transactions = max_transactions
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis | None:
        if redis is None:
            return None
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                )
            except Exception:
                return None
        return self._client

    def _key(self, pan_hash: str) -> str:
        return f"velocity:{pan_hash}"

    async def check(
        self,
        pan_hash: str,
        amount_minor: int,
        window_seconds: int | None = None,
    ) -> bool:
        """
        Registra tentativa e verifica se está dentro do limite.
        Retorna True se OK (pode autorizar), False se excesso (rejeitar).
        """
        client = await self._get_client()
        if client is None:
            return True  # fail-open
        key = self._key(pan_hash)
        window = window_seconds or self.window_seconds
        try:
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            results = await pipe.execute()
            count = results[0]
            return count <= self.max_transactions
        except Exception:
            return True  # fail-open

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None


def create_velocity_check_fn(redis_url: str, window_seconds: int = 300) -> Callable[..., Awaitable[bool]]:
    """Factory para função de velocity check usada no AntifraudHandler."""
    svc = RedisVelocityService(redis_url, window_seconds=window_seconds)

    async def check(pan_hash: str, amount_minor: int, window_seconds_param: int) -> bool:
        return await svc.check(pan_hash, amount_minor, window_seconds_param)

    return check
