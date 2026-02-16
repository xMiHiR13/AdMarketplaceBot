import requests

from asyncio import TimeoutError

from config import MAIN_APP_DOMAIN, MAIN_APP_API_KEY, ADS_CHANNEL

from MABot import MABot, app
from MABot.cache import CONVERSATIONS

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton


@app.on_callback_query(filters.regex(r"submitAd"))
async def _submit_ad_cbq(bot: MABot, cbq: CallbackQuery):
    if cbq.from_user.id in CONVERSATIONS:
        await cbq.answer("⛔ You can't submit ad while communicating.", show_alert=True)
        return

    try:
        deal_id = cbq.data.split("|")[1]
    except:
        return
    finally:
        try:
            await cbq.answer()
        except:
            pass

    try:
        ad_msg = await bot.ask(cbq.from_user.id, "🔽 <b>Send/Forward the ad here:</b>", timeout=120)
    except TimeoutError:
        await cbq.message.reply_text("Timeout! Try Again.")
        return

    if ad_msg.media_group_id:
        await cbq.message.reply_text(
            text="⛔ Media group messages are not supported yet!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Resubmit Ad", callback_data=f"submitAd|{deal_id}")]])
        )
        return

    msg = await ad_msg.forward(ADS_CHANNEL)

    data = {
        "chatId": msg.chat.id,
        "messageId": msg.id
    }

    processing_msg = await cbq.message.reply_text("🔄️ <b>Processing...</b>")

    response = requests.patch(
        url=f"{MAIN_APP_DOMAIN}/api/deals/{deal_id}/submit-ad",
        json=data,
        headers={ "x-api-key": MAIN_APP_API_KEY }
    )

    data = response.json()

    if 200 <= response.status_code < 300:
        await cbq.message.reply_text(
            text="✅ <b>Ad Submitted!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Deal", url=f"https://t.me/{bot.me.username}/deals?startapp={deal_id}")]])
        )
    else:
        await cbq.message.reply_text(f"⛔ {data['message']}")

    try:
        await processing_msg.delete()
    except:
        pass
