# /utils/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os

#MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://host.docker.internal:27017")


# Async connection
async def get_mongo_client() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(MONGO_URI)
    try:
        await client.admin.command("ismaster")
        return client
    except ConnectionFailure:
        raise Exception("Cannot connect to MongoDB")

# Sync connection (for testing purposes)
def get_mongo_client_sync() -> MongoClient:
    client = MongoClient(MONGO_URI)
    try:
        client.admin.command("ismaster")
        return client
    except ConnectionFailure:
        raise Exception("Cannot connect to MongoDB")
