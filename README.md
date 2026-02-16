# 🚀 Telegram Ad Marketplace Bot

Telegram bot for managing an **Ad Marketplace system**.

Main purpose:

- Command-based workflow
- 1-on-1 chat between advertiser and publisher
- Add / view ads for deals
- Automated cron jobs
- Secure ad storage

Repository:  
https://github.com/xMiHiR13/AdMarketplaceBot

---

# ⚙️ Environment Variables

Create a `.env` file and configure:

## 🔑 Telegram

| Variable | Description |
|----------|------------|
| `API_ID` | Telegram API ID |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Bot token from @BotFather |

---

## 🗄 Database

| Variable | Description |
|----------|------------|
| `MONGO_URL` | MongoDB connection string |
| `DB_NAME` | Database name (default: `TgAdMarketplace`) |

---

## 🌐 Main App Integration

| Variable | Description |
|----------|------------|
| `MAIN_APP_DOMAIN` | Main app base URL |
| `MAIN_APP_API_KEY` | API key for main app authentication |

---

## 👮 Access Control

| Variable | Description |
|----------|------------|
| `OWNER_ID` | Bot owner Telegram user ID |
| `MODS_USERS` | List of moderator user IDs |

---

## 📢 Ads Channel

| Variable | Description |
|----------|------------|
| `ADS_CHANNEL` | Private channel ID where approved ads are stored temporarily |

**Why Ads Channel?**

Approved ads are copied to this channel.  
Even if a user edits or deletes their original message later,  
the stored version remains unchanged and protected from malicious modifications.

---

## 🔄 Git Auto Update

| Variable | Description |
|----------|------------|
| `UPSTREAM_REPO` | GitHub repository URL |
| `UPSTREAM_BRANCH` | Branch for updates (default: `main`) |
| `GIT_TOKEN` | GitHub token (if required) |

---

## 💎 TON (Payments)

| Variable | Description |
|----------|------------|
| `MNEMONIC` | TON wallet seed phrase (space separated words) |
| `TONCENTER_API_KEY` | TON Center API key |
| `IS_TESTNET` | `true` for testnet, `false` for mainnet |

---

# 🛠 Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/xMiHiR13/AdMarketplaceBot.git
cd AdMarketplaceBot
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Setup `.env`

Example:

```env
API_ID=
API_HASH=
BOT_TOKEN=
MONGO_URL=
OWNER_ID=
MNEMONIC=
TONCENTER_API_KEY=
IS_TESTNET=false
```

---

# ▶️ Run Bot

You can start the bot using:

```bash
bash start
```

or

```bash
python -m MABot
```

---

# ⏰ Cron Jobs

Handles:

- Stalled deals cleanup
- Verify posted ads
- Post ads at scheduled time

---

# 📄 License

This project is licensed under the **GNU General Public License (GPL)**.

See the `LICENSE` file for full details.