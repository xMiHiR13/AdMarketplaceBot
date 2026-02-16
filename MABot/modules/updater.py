import os

from config import OWNER_ID, UPSTREAM_REPO, UPSTREAM_BRANCH

from typing import Union
from datetime import datetime

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

from MABot import app
from MABot.cache import CVARS
from MABot.core.mongo import close_mongodb
from MABot.utils.data import UPDATE_BOT_BUTTON

from pyrogram import filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import Message, CallbackQuery, LinkPreviewOptions


async def _update_bot(bot, update: Union[Message, CallbackQuery]):
    message = update.message if isinstance(update, CallbackQuery) else update

    if CVARS.IS_UPDATING:
        await message.reply_text("🔄️ <b>ᴜᴘᴅᴀᴛɪɴɢ ɪɴ ᴘʀᴏᴄᴇss...</b>\n\nᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟ ᴛʜᴇ ᴜᴘᴅᴀᴛᴇ ғɪɴɪsʜᴇᴅ.")
        return

    if isinstance(update, Message):
        # Force Update the Bot
        if CVARS.IS_BROADCASTING:
            await message.reply_text("⛔ <b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ɪɴ ᴘʀᴏᴄᴇss...</b>\n\nᴄʟɪᴄᴋ ᴏɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ғᴏʀᴄᴇ ᴜᴘᴅᴀᴛᴇ ᴛʜᴇ ʙᴏᴛ.", reply_markup=UPDATE_BOT_BUTTON)
            return
        response = await message.reply_text("ᴄʜᴇᴄᴋɪɴɢ ꜰᴏʀ ᴀᴠᴀɪʟᴀʙʟᴇ ᴜᴘᴅᴀᴛᴇs...")
    else:
        response = await message.edit_text("ᴄʜᴇᴄᴋɪɴɢ ꜰᴏʀ ᴀᴠᴀɪʟᴀʙʟᴇ ᴜᴘᴅᴀᴛᴇs...")

    CVARS.IS_UPDATING = True

    try:
        repo = Repo()
    except GitCommandError:
        CVARS.IS_UPDATING = False
        await response.edit_text("⛔ <b>ɢɪᴛ ᴄᴏᴍᴍᴀɴᴅ ᴇʀʀᴏʀ.</b>")
        return
    except InvalidGitRepositoryError:
        CVARS.IS_UPDATING = False
        await response.edit_text("⚠️ <b>ɪɴᴠᴀʟɪᴅ ɢɪᴛ ʀᴇᴘsɪᴛᴏʀʏ.</b>")
        return

    # Fetch upstream
    repo.remotes.origin.fetch(UPSTREAM_BRANCH)

    local_commit = repo.head.commit
    remote_commit = repo.remotes.origin.refs[UPSTREAM_BRANCH].commit

    if local_commit.hexsha == remote_commit.hexsha:
        CVARS.IS_UPDATING = False
        await response.edit_text("ʙᴏᴛ ɪs ᴜᴩ-ᴛᴏ-ᴅᴀᴛᴇ ᴡɪᴛʜ ᴜᴩsᴛʀᴇᴀᴍ ʀᴇᴩᴏ !")
        return

    updates = ""
    commits = list(repo.iter_commits(f"{local_commit}..{remote_commit}"))

    if not commits:
        updates += "<b>⚠️ ʜɪsᴛᴏʀʏ ᴅɪᴠᴇʀɢᴇᴅ — ʀᴇsᴇᴛᴛɪɴɢ ᴛᴏ ᴜᴩsᴛʀᴇᴀᴍ...</b>\n\n"
    else:
        # Get total commits in upstream branch up to each new commit
        all_commits_upstream = list(repo.iter_commits(f"origin/{UPSTREAM_BRANCH}"))
        total_in_upstream = len(all_commits_upstream)

        # New commits are the ones not in local — show their real position (newest first)
        for index, commit in enumerate(commits):  # commits are already newest first
            # Position = total in upstream minus how many are after this commit
            position = total_in_upstream - index
            date = datetime.fromtimestamp(commit.committed_date)
            day = date.day
            ordinal = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

            updates += (
                f"<b>➣ #{position}: <a href='{UPSTREAM_REPO}/commit/{commit.hexsha}'>{commit.summary.strip()}</a></b>\n"
                f"\t\t\t\t<b>➥ ʙʏ:</b> {commit.author.name}\n"
                f"\t\t\t\t<b>➥ ᴏɴ:</b> {day}{ordinal} {date.strftime('%b %Y')}\n\n"
            )

    _final_updates_ = "<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n<b><u>ᴜᴩᴅᴀᴛᴇs:</u></b>\n\n" + updates

    if len(_final_updates_) > 4096:
        with open("cache/Updates.txt", "w") as file:
            file.write(_final_updates_)
        try:
            mx = await message.reply_document("cache/Updates.txt", file_name="Updates.txt")
        except:
            pass
        os.remove("cache/Updates.txt")
        _final_updates_ = f"<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n<b><u>ᴜᴩᴅᴀᴛᴇs:</u></b> <a href='{mx.link}'>ᴄʜᴇᴄᴋ ᴜᴩᴅᴀᴛᴇs</a>"

    try:
        await response.edit_text(_final_updates_, link_preview_options=LinkPreviewOptions(is_disabled=True))
    except:
        pass

    # Safely reset to upstream — handles --amend, force push, conflicts
    if repo.is_dirty(untracked_files=True):
        repo.git.stash('push', '-m', 'auto-stash-before-update')

    repo.git.reset('--hard', f'origin/{UPSTREAM_BRANCH}')

    # Closing Connections
    await close_mongodb()

    try:
        await response.edit_text(f"{_final_updates_}ʙᴏᴛ ᴜᴩᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ! ɴᴏᴡ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ ᴍɪɴᴜᴛᴇs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ ʀᴇsᴛᴀʀᴛs ᴀɴᴅ ᴩᴜsʜ ᴄʜᴀɴɢᴇs !", link_preview_options=LinkPreviewOptions(is_disabled=True))
    except:
        pass

    os.system("pip3 install --no-cache-dir -U -r requirements.txt")
    os.system(f"kill -9 {os.getpid()} && bash start")
    exit()

app.add_handler(MessageHandler(_update_bot, filters=(filters.command('update') & filters.user(OWNER_ID) & ~filters.forwarded)))
app.add_handler(CallbackQueryHandler(_update_bot, filters=(filters.regex(r'updateBot') & filters.user(OWNER_ID))))