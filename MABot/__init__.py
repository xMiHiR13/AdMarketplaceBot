from config import BOT_TOKEN

from MABot.core.git import git
from MABot.core.bot import MABot

app = MABot(bot_name="MABot", bot_token=BOT_TOKEN)

git()
