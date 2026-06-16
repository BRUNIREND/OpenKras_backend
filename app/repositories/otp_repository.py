# app/repositories/otp_repository.py
from redis.asyncio import Redis

class OTPRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _get_key(self, email: str) -> str:
        """Внутренний хелпер для формирования ключа"""
        return f"otp:email:{email}"

    async def save_otp(self, email: str, code: str, expire_seconds: int) -> None:
        await self.redis.set(self._get_key(email), code, ex=expire_seconds)

    async def get_otp(self, email: str) -> str | None:
        """Получает сохраненный OTP код или возвращает None"""
        return await self.redis.get(self._get_key(email))

    async def delete_otp(self, email: str) -> None:
        """Удаляет OTP код из базы данных Redis"""
        await self.redis.delete(self._get_key(email))


