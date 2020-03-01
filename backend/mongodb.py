import logging

from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGODB_URL, MONGO_DBNAME


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


def get_mongo_connection():
    """Mongo connection for usage without app context"""
    task_db = DataBase()
    task_db.client = AsyncIOMotorClient(
        str(MONGODB_URL),
        maxPoolSize=10,
        minPoolSize=1,
    )

    return task_db.client[MONGO_DBNAME]


async def connect_to_mongo(app):
    logging.info("Connecting to Mongo...")
    db.client = AsyncIOMotorClient(str(MONGODB_URL),
                                   maxPoolSize=100,
                                   minPoolSize=10)
    app.mongodb = db.client[MONGO_DBNAME]
    logging.info("Connected to Mongo.")


async def close_mongo_connection():
    logging.info("Closing Mongo connection...")
    db.client.close()
    logging.info("Closed Mongo connection.")
