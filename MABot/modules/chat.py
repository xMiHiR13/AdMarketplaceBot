import asyncio

from time import time
from bson import ObjectId

from pyrogram import filters
from pyrogram.errors import UserIsBlocked
from pyrogram.types import Message, ReplyParameters, CallbackQuery, LinkPreviewOptions, InlineKeyboardMarkup, InlineKeyboardButton

from MABot import MABot, app
from MABot.core.mongo import DealsCol
from MABot.types import DealStatus, DealRole
from MABot.cache import CONVERSATIONS, CONVERSATIONS_LAST_ACTIVITY, CONVERSATIONS_NOTIFICATION


@app.on_message(filters.private & filters.incoming, group=-1)
async def _incoming_message_handler(bot: MABot, message: Message):
    my_id = message.from_user.id

    if my_id in bot._pending_asks:
        future = bot._pending_asks[my_id]
        future.set_result(message)
        await message.stop_propagation()
        return

    if message.text.startswith("/end"):
        if my_id in CONVERSATIONS:
            partner_id = CONVERSATIONS[my_id]
            del CONVERSATIONS[my_id]
            if CONVERSATIONS.get(partner_id) == my_id:
                del CONVERSATIONS[partner_id]
            await message.reply_text("⏳ Conversation stopped.")
        else:
            await message.reply_text("You're not connected in any conversation.")
        await message.stop_propagation()
        return

    if my_id in CONVERSATIONS:
        partner_id = CONVERSATIONS[my_id]
        try:
            if message.media_group_id:
                await message.copy_media_group(partner_id)
            else:
                await message.copy(partner_id)
        except UserIsBlocked:
            del CONVERSATIONS[my_id]
            del CONVERSATIONS[partner_id]
            del CONVERSATIONS_LAST_ACTIVITY[tuple(sorted([my_id, partner_id]))]
            await message.reply_text(
                text=f"⛔ <b>User has blocked the bot!</b>\n\nEnding this conversation.",
                reply_parameters=ReplyParameters(message_id=message.id)
            )
        except Exception as e:
            await message.reply_text(
                text=f"⛔ <b>Failed to send this message!</b>\n\nError = {type(e).__name__}",
                reply_parameters=ReplyParameters(message_id=message.id)
            )
        else:
            CONVERSATIONS_LAST_ACTIVITY[tuple(sorted([my_id, partner_id]))] = int(time())
        await message.stop_propagation()
        return


@app.on_callback_query(filters.regex(r"startChat"))
async def _start_chat_cbq(bot: MABot, cbq: CallbackQuery):
    my_id = cbq.from_user.id

    try:
        cmd, deal_id = cbq.data.split("|")
    except:
        await cbq.answer()
        return

    deal = await DealsCol.find_one({"_id": ObjectId(deal_id)})

    if not deal:
        await cbq.edit_message_text("⛔ Deal not found.")
        await cbq.answer()
        return

    if deal['status'] in DealStatus.terminal_statuses():
        await cbq.edit_message_text("⛔ This deal is no longer active.")
        await cbq.answer()
        return

    my_role = DealRole.ADVERTISER if (my_id == deal["advertiserId"]) else DealRole.PUBLISHER if (my_id == deal['publisherId'] or my_id in deal.get('managerIds', [])) else None

    if not my_role:
        await cbq.edit_message_text("⛔ You're not allowed.")
        await cbq.answer()
        return

    if my_role == DealRole.ADVERTISER:
        partner_role = DealRole.PUBLISHER.value
        partner_id = int(deal['publisherId'])
    elif my_role == DealRole.PUBLISHER:
        partner_id = int(deal['advertiserId'])
        partner_role = DealRole.ADVERTISER.value
    else:
        await cbq.edit_message_text("⛔ Invalid receiver role.")
        await cbq.answer()
        return

    if my_id in CONVERSATIONS:
        if cmd == "startChatForce":
            current_partner_id = CONVERSATIONS[my_id]
            del CONVERSATIONS[my_id]
            if CONVERSATIONS.get(current_partner_id) == my_id:
                del CONVERSATIONS[current_partner_id]
        else:
            await cbq.answer("⛔ You're already connected with someone.", show_alert=True)
            return

    if partner_id in CONVERSATIONS:
        notified_at = CONVERSATIONS_NOTIFICATION.get(f"{my_id}_{partner_id}", 0)
        if int(time()) - notified_at < 300:
            await cbq.answer("⛔ Receiver is already notified.", show_alert=True)
            return
        try:
            await bot.send_message(
                chat_id=partner_id,
                text=f"🗨️ <b>Conversation request from {my_role.value.capitalize()} of <a href='https://t.me/{bot.me.username}/deals?startapp={deal_id}'>deal</a>.</b>",
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Start Chat", callback_data=f"startChatForce|{deal_id}")]])
            )
            await cbq.answer("⛔ Receiver is not idle.\n\nHe/she has been notified for your conversation request.", show_alert=True)
            CONVERSATIONS_NOTIFICATION[f"{my_id}_{partner_id}"] = int(time())
        except Exception as e:
            await cbq.answer(f"⛔ Failed to send conversation request to receiver.\n\nError = {type(e).__name__}")
        return
    
    CONVERSATIONS[my_id] = partner_id
    CONVERSATIONS[partner_id] = my_id
    CONVERSATIONS_LAST_ACTIVITY[tuple(sorted([my_id, partner_id]))] = int(time())

    await cbq.message.reply_text(f"✅ You're connected to {partner_role} of <a href='https://t.me/{bot.me.username}/deals?startapp={deal_id}'>deal</a>.\n\nYou can start messaging.\n\nEnter /end to end the conversation.", link_preview_options=LinkPreviewOptions(is_disabled=True))
    try:
        await bot.send_message(partner_id, f"✅ You're connected to {my_role.value} of <a href='https://t.me/{bot.me.username}/deals?startapp={deal_id}'>deal</a>.\n\nYou can start messaging.\n\nEnter /end to end the conversation.", link_preview_options=LinkPreviewOptions(is_disabled=True))
    except:
        pass
    await cbq.answer()


async def _auto_clear_inactive_conversations():
    while True:
        await asyncio.sleep(60)

        for key, last_activity in CONVERSATIONS_LAST_ACTIVITY.copy().items():
            if int(time()) - last_activity > 300:
                del CONVERSATIONS_LAST_ACTIVITY[key]
                user1_id, user2_id = key
                if user1_id in CONVERSATIONS:
                    try:
                        del CONVERSATIONS[user1_id]
                    except:
                        pass
                    try:
                        await app.send_message(user1_id, "⚠️ Your conversation has ended due to inactivity.")
                    except:
                        pass
                if user2_id in CONVERSATIONS:
                    try:
                        del CONVERSATIONS[user2_id]
                    except:
                        pass
                    try:
                        await app.send_message(user2_id, "⚠️ Your conversation has ended due to inactivity.")
                    except:
                        pass

asyncio.create_task(_auto_clear_inactive_conversations())
