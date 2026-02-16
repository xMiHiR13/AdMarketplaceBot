from asyncio import sleep

from config import OWNER_ID

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from MABot import MABot, app
from MABot.cache import CVARS
from MABot.core.mongo import UsersCol


@app.on_message(filters.command(["broadcast", "gcast", "gcastx"]) & filters.user(OWNER_ID) & ~filters.forwarded)
async def _braodcast_message(bot: MABot, message: Message):
    if CVARS.IS_BROADCASTING:
        await message.reply_text("<b><i>ᴀʟʀᴇᴀᴅʏ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...</i></b>")
        return

    if not message.reply_to_message:
        await message.reply_text("<b>Command Usage:</b>\n/broadcast [Reply to a Message]\n/gcastx [Reply to a Message]")
        return

    message_id = message.reply_to_message.id
    chat_id = message.chat.id

    if message.command[0] == "gcastx":
        markup = message.reply_to_message.reply_markup
        copy = True
    else:
        copy = False

    CVARS.IS_BROADCASTING = True
    await message.reply_text("<b><i>sᴛᴀʀᴛᴇᴅ ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛ...</i></b>")
    bot_users = [user_doc["_id"] async for user_doc in UsersCol.find({})]
    ind = 0

    for user_id in bot_users:
        if not CVARS.IS_BROADCASTING:
            return

        if ind and ind % 300 == 0:
            await sleep(180)

        try:
            if copy:
                await bot.copy_message(user_id, chat_id, message_id, reply_markup=markup)
            else:
                await bot.forward_messages(user_id, chat_id, message_id)
        except FloodWait as e:
            if e.value > 200:
                continue
            await sleep(e.value)
        except Exception as e:
            pass
        else:
            ind += 1
            await sleep(1)

    CVARS.IS_BROADCASTING = False
    await message.reply_text(f"<b>ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ ᴛᴏ {ind} ᴜsᴇʀs.</b>")


@app.on_message(filters.command(["stopbroadcast", "stopgcast"]) & filters.user(OWNER_ID))
async def _stop_braodcast(bot: MABot, message: Message):
    if CVARS.IS_BROADCASTING:
        CVARS.IS_BROADCASTING = False
        await message.reply_text("✅ <b><i>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ sᴛᴏᴘᴘᴇᴅ...</i></b>")
    else:
        await message.reply_text("<b><i>ɴᴏᴛʜɪɴɢ ɪs ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ.</i></b>")