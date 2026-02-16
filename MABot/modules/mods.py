import sys
import asyncio
import traceback

from config import OWNER_ID

from MABot import MABot, app

from os import remove
from io import StringIO

from pyrogram import filters
from pyrogram.types import Message


async def aexec(code, client, message):
    exec_env = {
        "client": client,
        "message": message,
        "__name__": "__main__",
    }

    func_code = (
        "async def __aexec(client, message):\n"
        + "\n".join(f"    {line}" for line in code.split("\n"))
    )

    exec(func_code, exec_env)   # compile into our own environment
    return await exec_env["__aexec"](client, message)


@app.on_message(filters.command("eval") & filters.user(OWNER_ID) & ~filters.forwarded)
async def executor(bot: MABot, message: Message):
    try:
        cmd = message.text.split(None, maxsplit=1)[1]
    except IndexError:
        await message.reply_text("<b>ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴɴᴀ ᴇxᴇᴄᴜᴛᴇ ?</b>")
        return

    mx = await message.reply_text("🔄️ <b>ᴘʀᴏᴄᴇssɪɴɢ...</b>")
    await asyncio.sleep(1)

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, bot, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    evaluation = evaluation.strip()
    await mx.delete()

    if len(evaluation) > 4000:
        with open("Output.txt", "w+", encoding="utf8") as out_file:
            out_file.write(f"⥤ ɪɴᴘᴜᴛ :\n\n{cmd}\n\n\n⥤ ʀᴇsᴜʟᴛ :\n\n{evaluation}")
        await message.reply_document(document="Output.txt", caption=f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n<code>Attached Document</code>")
        remove("Output.txt")
        await message.delete()
    else:
        final_output = f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n\n<pre language='python'>{evaluation}</pre>"
        await message.reply_text(final_output)