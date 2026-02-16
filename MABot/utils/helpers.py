import speedtest

from pyrogram.types import Message


def testspeed(message: Message):
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        message.edit_text("<b>⇆ ʀᴜɴɴɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ sᴩᴇᴇᴅᴛᴇsᴛ...</b>")
        test.download()
        message.edit_text("<b>⇆ ʀᴜɴɴɪɴɢ ᴜᴩʟᴏᴀᴅ sᴩᴇᴇᴅᴛᴇsᴛ...</b>")
        test.upload()
        test.results.share()
        message.edit_text("<b>↻ sʜᴀʀɪɴɢ sᴩᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs...</b>")
        return test.results.dict()
    except Exception as e:
        message.edit_text(f"⛔ <b>ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ.</b>\n\nError = <code>{type(e).__name__}</code>\nErrorData = <code>{str(e)}</code>")
        return
