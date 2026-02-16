from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, WebAppInfo

# ------------- STRINGS -------------

START_IMAGE = "https://telegra.ph/file/e3acc2a714cd55c22d188-b60c03a10cf24e86cb.jpg"

START_TEXT = """<b>Welcome to TG Ad Marketplace — connecting advertisers and publishers for fast, transparent, and secure ad deals. 🚀</b>"""

PING_TEXT = """<b>❕ᴘɪɴɢ ᴛᴀꜱᴋ ᴇxᴇᴄᴜᴛᴇᴅ</b>
<b>   × ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{0}ᴍs</code>
<b>   × ᴜᴘᴛɪᴍᴇ:</b> <code>{1}</code>

<b>❕sʏsᴛᴇᴍ sᴛᴀᴛs</b>
<b>   × ᴄᴘᴜ:</b> <code>{4}</code>
<b>   × ᴅɪsᴋ:</b> <code>{2}</code>
<b>   × ʀᴀᴍ:</b> <code>{3}</code>"""


# ------------- BUTTONS -------------

START_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🏪 Ad Marketplace", web_app=WebAppInfo(url="https://ad-marketplace-x.vercel.app/"))
    ],
    [
        InlineKeyboardButton("📄 My Deals", web_app=WebAppInfo(url="https://ad-marketplace-x.vercel.app/deals")),
        InlineKeyboardButton("👤 My Profile", web_app=WebAppInfo(url="https://ad-marketplace-x.vercel.app/profile"))
    ]
])

UPDATE_BOT_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton('Update Bot', callback_data="updateBot")]])

RESTART_BOT_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton('Restart Bot', callback_data="restartBot")]])

# ------------- MABot COMMANDS -------------

BOT_COMMANDS = [
    BotCommand("start", "Start The Bot")
]