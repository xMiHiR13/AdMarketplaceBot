from time import time
from pyrogram import filters

from config import OWNER_ID, MODS_USERS

MODS = filters.user([OWNER_ID] + MODS_USERS)

_boot_ = time()
