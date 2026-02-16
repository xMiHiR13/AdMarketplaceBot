from asyncio import sleep

from config import MONGO_URL, DB_NAME

from MABot.logging import LOGGER

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError


_mongo_async_ = AsyncIOMotorClient(MONGO_URL)

# Mongo Collections
UsersCol = _mongo_async_[DB_NAME]['users']
ChannelsCol = _mongo_async_[DB_NAME]['channels']
DealsCol = _mongo_async_[DB_NAME]['deals']
PaymentsCol = _mongo_async_[DB_NAME]['payments']

async def check_mongodb():
    while True:
        try:
            await _mongo_async_.admin.command("ping")
            LOGGER(__name__).info("MongoDB Connection Successful!")
            break
        except ServerSelectionTimeoutError:
            LOGGER(__name__).warning(f"Failed to connect MongoDB. Connecting again in 5 minutes...")
            await sleep(300)

async def close_mongodb():
    try:
        await _mongo_async_.close()
    except:
        pass
    LOGGER(__name__).info("MongoDB Connection Closed!")
