import os
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    def __init__(self):
        self.client = None
        self.database = None

    def connect(self):
        if self.client is None:
            uri = (
                f"mongodb://{os.getenv('MONGO_INITDB_ROOT_USERNAME')}:"
                f"{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@"
                f"{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}"
            )

            self.client = AsyncIOMotorClient(uri)
            self.database = self.client[os.getenv("MONGO_DB")]

            print("? Connected to MongoDB")

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            print("? MongoDB connection closed")


db_mongo = MongoDB()