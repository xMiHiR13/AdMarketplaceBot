import asyncio

from MABot.logging import LOGGER

from bson import ObjectId
from typing import Optional, Dict, Any
from pymongo.errors import PyMongoError
from datetime import datetime, timezone, timedelta

from MABot import app
from MABot.types import DealStatus
from MABot.core.ton import send_ton
from MABot.core.mongo import DealsCol


# AUTO POST TASK

async def find_earliest_unposted_scheduled_deal() -> Optional[Dict[str, Any]]:
    """
    Find the deal with the earliest (smallest) postAt among all still-unposted 'scheduled' deals.
    No maximum lateness limit — will pick even very old scheduled posts.
    Returns None if no such deal exists.
    """
    try:
        pipeline = [
            {
                "$match": {
                    "status": DealStatus.SCHEDULED.value,
                    "schedule.postAt": {"$exists": True},
                    "schedule.post": {"$exists": False},
                }
            },
            # sort by postAt ascending -> earliest first
            {"$sort": {"schedule.postAt": 1}},
            {"$limit": 1},
        ]

        cursor = DealsCol.aggregate(pipeline)
        docs = await cursor.to_list(length=1)
        return docs[0] if docs else None

    except PyMongoError as e:
        LOGGER(__name__).error(f"Error finding earliest scheduled deal: {e}")
        return None


async def post_deal_ads_task():
    LOGGER(__name__).info("post_deal_ads_task Started!")

    while True:
        if not app.is_connected:
            await asyncio.sleep(5)
            continue
        try:
            deal = await find_earliest_unposted_scheduled_deal()
            if not deal:
                await asyncio.sleep(60)
                continue

            post_at: datetime = deal["schedule"]["postAt"]
            post_at = post_at.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            seconds_left = (post_at - now).total_seconds()

            deal_id = str(deal["_id"])
            chat_id = int(deal["channel"]["chatId"])
            ad = deal["ad"]

            if seconds_left > 0:
                # Future post -> wait until the time
                await asyncio.sleep(seconds_left)
            else:
                # Already due or overdue -> post immediately
                overdue = abs(seconds_left)
                if overdue > 3600:  # more than 1 hour late
                    LOGGER(__name__).warning(f"Posting significantly overdue deal {deal_id} ({int(overdue / 3600)}h {int((overdue % 3600)/60)}min late)")
                else:
                    LOGGER(__name__).info(f"Posting due deal {deal_id} (on time or slightly late)")

            try:
                sent_message = await app.copy_message(chat_id, int(ad['chatId']), int(ad['messageId']))
            except Exception as posting_exc:
                await DealsCol.update_one(
                    {"_id": ObjectId(deal["_id"])},
                    {
                        "$set": {
                            "status": DealStatus.POSTING_FAILED.value,
                            "updatedAt": datetime.now(timezone.utc),
                        }
                    }
                )
                LOGGER(__name__).error(f"Posting failed for deal {deal_id}: {posting_exc}")
            else:
                LOGGER(__name__).info(f"Successfully posted deal #{deal_id} ad to chat {chat_id}")
                # Mark as posted
                await DealsCol.update_one(
                    {"_id": ObjectId(deal["_id"])},
                    {
                        "$set": {
                            "schedule.post.messageId": sent_message.id,
                            "schedule.post.postedAt": datetime.now(timezone.utc),
                            "status": DealStatus.POSTED.value,
                            "updatedAt": datetime.now(timezone.utc),
                        }
                    }
                )

        except Exception as loop_exc:
            LOGGER(__name__).exception(f"Unexpected error in post_deal_ads_task: {loop_exc}")

        await asyncio.sleep(60)

asyncio.create_task(post_deal_ads_task())


# STALLED DEALS CLEANUP TASK

async def stalled_deals_cleanup_task():
    LOGGER(__name__).info("stalled_deals_cleanup_task Started!")

    while True:
        try:
            one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            query = {
                "updatedAt": {"$lte": one_week_ago},
                "status": {"$nin": list(DealStatus.terminal_statuses())}
            }
            stalled = await DealsCol.find(query).to_list(None)

            if stalled:
                LOGGER(__name__).info(f"Found {len(stalled)} inactive deals (no update >7 days)")
                for deal in stalled:
                    deal_id = str(deal["_id"])
                    days_inactive = (datetime.now(timezone.utc) - deal["updatedAt"].replace(tzinfo=timezone.utc)).total_seconds() / 86400
                    await DealsCol.update_one(
                        {"_id": ObjectId(deal["_id"])},
                        {
                            "$set": {
                                "status": DealStatus.CANCELLED.value,
                                "updatedAt": datetime.now(timezone.utc)
                            }
                        }
                    )
                    LOGGER(__name__).info(f"Cancelled inactive deal {deal_id} ({days_inactive:.1f} days no activity)")
                    await asyncio.sleep(0.5)
            
            await asyncio.sleep(30 * 60)  # check every 30 minutes
            
        except Exception as e:
            LOGGER(__name__).error(f"Error in stalled deals cleanup task: {e}")
            await asyncio.sleep(300)

asyncio.create_task(stalled_deals_cleanup_task())


# POST VERIFY TASK

async def post_verify_task():
    LOGGER(__name__).info("post_verify_task Started!")

    while True:
        if not app.is_connected:
            await asyncio.sleep(5)
            continue

        query = {
            "status": "posted",
            "schedule.post": {"$exists": True},
            "$expr": {
                "$lte": [
                    {
                        "$dateAdd": {
                            "startDate": "$schedule.post.postedAt",
                            "unit": "day",
                            "amount": "$duration"
                        }
                    },
                    datetime.now(timezone.utc)
                ]
            }
        }
        try:
            posted_deals = await DealsCol.find(query).to_list(length=None)
            for deal in posted_deals:
                channel_id = int(deal['channel']['chatId'])
                message_id = int(deal['schedule']['post']['messageId'])
                is_deleted = False
                is_edited = False
                try:
                    message = await app.get_messages(channel_id, message_id)
                    if message.empty:
                        is_deleted = True
                    elif message.edit_date and not message.edit_hidden:
                        is_edited = True
                except Exception as e:
                    is_deleted = True
                try:
                    await DealsCol.update_one(
                        { "_id": ObjectId(deal['_id']) },
                        { "$set": {
                            "schedule.verifiedAt": datetime.now(timezone.utc),
                            "status": DealStatus.REFUNDED_DELETE.value if is_deleted else DealStatus.REFUNDED_EDIT.value if is_edited else DealStatus.COMPLETED.value
                        }}
                    )
                except Exception as e:
                    LOGGER(__name__).error(f"Failed to update deal state: {e}")
                else:
                    if is_deleted or is_edited:
                        try:
                            await send_ton(str(deal['_id']), int(deal['advertiserId']), deal['payment']['senderAddress'], deal['price'])
                        except Exception as e:
                            LOGGER(__name__).error(f"Failed to refund: {e}")
                            continue
                        else:
                            try:
                                await DealsCol.update_one(
                                    { "_id": ObjectId(deal['_id']) },
                                    { "$set": { "payment.refundedAt": datetime.now(timezone.utc) }}
                                )
                            except Exception as e:
                                LOGGER(__name__).error(f"Failed to update deal refund state: {e}")
                await asyncio.sleep(1)
        except Exception as e:
            LOGGER(__name__).error(f"Error in post verify task: {e}")
            await asyncio.sleep(300)
        else:
            await asyncio.sleep(60)

asyncio.create_task(post_verify_task())
