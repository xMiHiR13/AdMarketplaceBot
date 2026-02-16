from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_ID = int(getenv("API_ID", "25981592"))
API_HASH = getenv("API_HASH", "709f3c9d34d83873d3c7e76cdd75b866")

BOT_TOKEN = getenv("BOT_TOKEN")

MONGO_URL = getenv("MONGO_URL")
DB_NAME = getenv("DB_NAME", "TgAdMarketplace")

MAIN_APP_DOMAIN = "http://localhost:3000"
MAIN_APP_API_KEY = "80f7d66c65b55ab088231e72a55f6a97c1885342f3fbe79f1ed7864de85b968f"

OWNER_ID = int(getenv("OWNER_ID"))
MODS_USERS = []  # List of moderators

ADS_CHANNEL = int(getenv("ADS_CHANNEL", "-1003842062286"))

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/xMiHiR13/AdMarketplaceBot")
UPSTREAM_BRANCH = "main"
GIT_TOKEN = getenv("GIT_TOKEN")

MNEMONIC = getenv("MNEMONIC").split()
TONCENTER_API_KEY = getenv("TONCENTER_API_KEY")
IS_TESTNET = getenv("IS_TESTNET", "false").lower() == "true"
