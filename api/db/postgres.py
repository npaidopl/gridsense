import os
import asyncpg


class PostgresDB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("POSTGRES_HOST"),
                port=int(os.getenv("POSTGRES_PORT", 5432)),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                database=os.getenv("POSTGRES_DB"),
                min_size=1,
                max_size=5,
            )
            print("✓ Connected to PostgreSQL")

    async def disconnect(self):
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            print("✓ PostgreSQL connection closed")


db_postgres = PostgresDB()