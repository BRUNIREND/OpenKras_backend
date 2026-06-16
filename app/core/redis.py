# app/core/redis.py
import redis.asyncio as aioredis

from app.core.config import settings

if settings.REDIS_PASSWORD:
    REDIS_URL = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
else:
    REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

# Пул создается прямо здесь. Коннекты откроются сами при первом запросе OTP
redis_pool = aioredis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)

async def get_redis():
    client = aioredis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        # Возвращает соединение обратно в пул, не закрывая сам пул
        await client.close()