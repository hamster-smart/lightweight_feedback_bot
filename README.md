# lightweight_feedback_bot

A minimal Telegram feedback bot. Users send messages — the admin receives them with a reply button and can respond directly from Telegram. No external services required.

---

## How it works

1. User sends a message to the bot
2. Bot forwards it to the admin with an inline **Reply** button
3. Admin clicks Reply, types a response
4. Bot delivers the reply back to the original user

Rate limiting and link filtering are handled by `security.py`.

---

## Setup

### Environment variables

| Variable | Description |
|---|---|
| `API_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | Your Telegram user ID (get it from [@userinfobot](https://t.me/userinfobot)) |

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

### Run with Docker Compose

```bash
docker compose up -d --build
```

### Run locally (without Docker)

```bash
pip install -r requirements.txt
python bulgaria_helps_bot.py
```

---

## Stack

- Python 3.11
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (telebot)
- python-dotenv
- Docker / Docker Compose

---

## Files

| File | Purpose |
|---|---|
| `feedback_bot.py` | Main bot logic |
| `security.py` | Rate limiting, link filtering, error handling |
| `Dockerfile` | Container build |
| `docker-compose.yml` | Compose deployment |
| `.env.example` | Environment variable template |
| `.dockerignore` | Excludes `.env` and cache from image |
