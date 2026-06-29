import os
import redis.asyncio as redis


class RedisDB:
    def __init__(self):
        self.client = None

    def connect(self):
        if self.client is None:
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST"),
                port=int(os.getenv("REDIS_PORT")),
                decode_responses=True,
            )

            print("? Connected to Redis")

    async def disconnect(self):
        if self.client is not None:
            await self.client.close()
            self.client = None
            print("? Redis connection closed")


db_redis = RedisDB()