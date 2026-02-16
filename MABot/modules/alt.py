import os
import psutil
import asyncio

from time import time
from typing import Union
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from MABot import MABot, app
from MABot.cache import CVARS
from MABot.mongodb import add_user
from MABot.misc import MODS, _boot_
from MABot.logging import LOG_FILE_NAME
from MABot.utils.helpers import testspeed
from MABot.core.mongo import close_mongodb
from MABot.utils.formatters import get_readable_time
from MABot.utils.data import START_IMAGE, START_TEXT, START_BUTTONS, PING_TEXT, RESTART_BOT_BUTTON


@app.on_message(filters.command('start') & filters.private)
async def _start(bot: MABot, message: Message):
    await message.reply_photo(START_IMAGE, caption=START_TEXT.format(bot.me.username), reply_markup=START_BUTTONS)

    if not message.forward_date:
        await add_user(message.from_user)


@app.on_message(filters.private & filters.service & ~filters.chat_shared)
async def _service_message_handler(bot: MABot, message: Message):
    if message.write_access_allowed:
        await add_user(message.from_user)


@app.on_message(filters.command('ping') & MODS & ~filters.forwarded)
async def _ping(_, message: Message):
    response = await message.reply_text("» <i>ʙᴜɪʟᴅᴇʀ</i>")

    start_time = datetime.now()
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage("/").percent

    CPU = f"{cpu_percent}%"
    RAM = f"{mem_percent}%"
    DISK = f"{disk_percent}%"
    UPTIME = await get_readable_time(int(time() - _boot_))
    RESPONSE_TIME = (datetime.now() - start_time).microseconds / 1000

    await response.edit_text(PING_TEXT.format(RESPONSE_TIME, UPTIME, DISK, RAM, CPU))


@app.on_message(filters.private & filters.command('speedtest') & MODS & ~filters.forwarded)
async def speedtest_function(bot: MABot, message: Message):
    m = await message.reply_text("⚡ ᴛʀʏɪɴɢ ᴛᴏ ᴄʜᴇᴄᴋ ᴜᴩʟᴏᴀᴅ ᴀɴᴅ ᴅᴏᴡɴʟᴏᴀᴅ sᴩᴇᴇᴅ...")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, testspeed, m)
    if result:
        output = f"""✯ <b>sᴩᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs</b> ✯
        
    <u><b>❥͜͡ᴄʟɪᴇɴᴛ :</b></u>
    <b>» <i>ɪsᴩ :</i></b> {result['client']['isp']}
    <b>» <i>ᴄᴏᴜɴᴛʀʏ :</i></b> {result['client']['country']}
    
    <u><b>❥͜͡sᴇʀᴠᴇʀ :</b></u>
    <b>» <i>ɴᴀᴍᴇ :</i></b> {result['server']['name']}
    <b>» <i>ᴄᴏᴜɴᴛʀʏ :</i></b> {result['server']['country']}, {result['server']['cc']}
    <b>» <i>sᴩᴏɴsᴏʀ :</i></b> {result['server']['sponsor']}
    <b>» <i>ʟᴀᴛᴇɴᴄʏ :</i></b> {result['server']['latency']}  
    <b>» <i>ᴩɪɴɢ :</i></b> {result['ping']}"""
        await bot.send_photo(chat_id=message.chat.id, photo=result["share"], caption=output)
        await m.delete()


@app.on_message(filters.private & filters.command('logs') & MODS & ~filters.forwarded)
async def _get_logs(bot, message: Message):
    if os.path.exists(LOG_FILE_NAME):
        x = await message.reply_text("🔄️ <b>ғᴇᴛᴄʜɪɴɢ ʟᴏɢs...</b>")
        await message.reply_document(LOG_FILE_NAME)
        await x.delete()
    else:
        await message.reply_text(f"⛔ <b>ʟᴏɢ ғɪʟᴇ <code>{LOG_FILE_NAME}</code> ᴅᴏᴇs ɴᴏᴛ ᴇxɪsᴛ.</b>")


async def _reboot_bot(_, update: Union[Message, CallbackQuery]):
    message = update.message if isinstance(update, CallbackQuery) else update

    if CVARS.IS_UPDATING:
        await message.reply_text("🔄️ <b>ᴜᴘᴅᴀᴛɪɴɢ ɪɴ ᴘʀᴏᴄᴇss...</b>\n\nᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟ ᴛʜᴇ ᴜᴘᴅᴀᴛᴇ ғɪɴɪsʜᴇᴅ.")
        return

    if CVARS.IS_RESTARTING:
        await message.reply_text("🔄️ <b>ʀᴇsᴛᴀʀᴛɪɴɢ ɪɴ ᴘʀᴏᴄᴇss...</b>\n\nᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟ ᴛʜᴇ ʀᴇsᴛᴀʀᴛ ғɪɴɪsʜᴇᴅ.")
        return

    if isinstance(update, Message):
        # Force Restart the Bot
        if CVARS.IS_BROADCASTING:
            await message.reply_text("⛔ <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ɪɴ ᴘʀᴏᴄᴇss...</b>\n\nᴄʟɪᴄᴋ ᴏɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ғᴏʀᴄᴇ ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.", reply_markup=RESTART_BOT_BUTTON)
            return
        response = await message.reply_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")
    else:
        response = await message.edit_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")

    CVARS.IS_RESTARTING = True

    # Closing Connections
    await close_mongodb()

    try:
        await response.edit_text("ʀᴇsᴛᴀʀᴛ ᴩʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ, ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ ᴍɪɴᴜᴛᴇs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ ʀᴇsᴛᴀʀᴛs.")
    except:
        pass
    os.system(f"kill -9 {os.getpid()} && bash start")

app.add_handler(MessageHandler(_reboot_bot, filters=(filters.command('restart') & MODS & ~filters.forwarded)))
app.add_handler(CallbackQueryHandler(_reboot_bot, filters=(filters.regex(r'restartBot') & MODS)))
