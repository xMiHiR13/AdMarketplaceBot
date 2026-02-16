import asyncio

from pyrogram import idle

from MABot import app
from MABot.core.dir import dir
from MABot.core.mongo import check_mongodb, close_mongodb

async def main():
    # Calling Functions
    await dir()
    await check_mongodb()

    # Starting The Bot
    await app.start()

    # Blocking Script
    await idle()

    # Closing Connections
    await close_mongodb()

    # Stopping The Bot
    await app.stop()

# Running Script
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
