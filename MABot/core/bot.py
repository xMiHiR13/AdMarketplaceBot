import sys
import asyncio

from config import API_ID, API_HASH, ADS_CHANNEL

from MABot.logging import LOGGER
from MABot.utils.data import BOT_COMMANDS

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import ChatAdministratorRights, Message


class MABot(Client):
    def __init__(self, bot_name: str, bot_token: str):
        super().__init__(
            name=bot_name,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins=dict(root="MABot/modules"),
            parse_mode=ParseMode.HTML,
            sleep_threshold=5,
            max_message_cache_size=3
        )
        self._pending_asks: dict[int, asyncio.Future] = {}  # Stores {chat_id: Future}

    async def start(self):
        await super().start()

        # Set Bot Commands
        is_set = await self.set_bot_commands(BOT_COMMANDS)
        if is_set:
            LOGGER(__name__).info(f"{self.me.username} Commands Set.")
        else:
            LOGGER(__name__).info(f"Failed to Set {self.me.username} Commands.")

        # Set Bot Privileges [For Channels]
        privileges = await self.get_bot_default_privileges(for_channels=True)
        if not privileges or not privileges.can_post_messages or not privileges.can_invite_users or not privileges.can_promote_members:
            await self.set_bot_default_privileges(
                ChatAdministratorRights(
                    can_manage_chat=True,
                    can_post_messages=True,
                    can_post_stories=True,
                    can_invite_users=True,
                    can_promote_members=True
                ),
                for_channels=True 
            )

        # Set Bot Privileges [For Groups]
        privileges = await self.get_bot_default_privileges(for_channels=False)
        if not privileges or not privileges.can_invite_users or not privileges.can_promote_members:
            await self.set_bot_default_privileges(
                ChatAdministratorRights(
                    can_manage_chat=True,
                    can_post_stories=True,
                    can_invite_users=True,
                    can_promote_members=True
                ),
                for_channels=False
            )

        try:
            await self.get_chat(ADS_CHANNEL)
        except Exception as e:
            LOGGER(__name__).warning(f"Failed to Access Ads Channel: {type(e).__name__}")
            sys.exit()
        else:
            # Bot Start Message
            LOGGER(__name__).info(f"{self.me.username} Started")

    async def stop(self):
        await super().stop()
        LOGGER(__name__).info(f"{self.me.username} Stopped!")

    async def ask(self, chat_id, question, reply_markup = None, timeout = 30) -> Message:
        if question:
            await self.send_message(chat_id, question, reply_markup=reply_markup)

        future = asyncio.get_event_loop().create_future()
        self._pending_asks[chat_id] = future

        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        finally:
            self._pending_asks.pop(chat_id, None)
