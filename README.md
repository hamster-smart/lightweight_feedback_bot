# lightweight_feedback_bot

A minimal Telegram feedback bot. Users send messages — the admin receives them and replies directly in Telegram. No external services, no database server required.

---

## How it works

1. User sends any text message to the bot
2. Bot forwards it to the admin with the user's name and ID
3. Admin replies to that forwarded message
4. Bot delivers the reply back to the original user

---

## Setup

### Environment variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | Your Telegram user ID (get it from [@userinfobot](https://t.me/userinfobot)) |

Copy `.env.example` to `.env` for local development:

```bash
cp .env.example .env
```

### Run locally

```bash
pip install -r requirements.txt
BOT_TOKEN=... ADMIN_ID=... python bulgaria_helps_bot.py
```

### Deploy to Render

1. Fork or push this repo to GitHub
2. Create a new **Background Worker** on [render.com](https://render.com)
3. Set `BOT_TOKEN` and `ADMIN_ID` in the Environment tab
4. Deploy — the `render.yaml` config handles the rest

---

## Stack

- Python 3.11+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 20.x
- SQLite (persistent message mapping, survives restarts)
- Render free tier (Background Worker)

---

## Notes

- Message-to-user mapping is stored in a local SQLite file (`message_map.db`), so admin replies work correctly after bot restarts
- On Render free tier, worker services don't spin down like web services do — no dummy HTTP server needed
