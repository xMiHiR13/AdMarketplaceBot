from time import time
from pyrogram.types import User

from MABot.core.mongo import UsersCol


async def add_user(user: User):
    await UsersCol.update_one(
        {"_id": user.id},
        {
            "$set": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "dc_id": user.dc_id
            },
            "$setOnInsert" : {
                "createdAt": int(time())
            }
        },
        upsert=True
    )
