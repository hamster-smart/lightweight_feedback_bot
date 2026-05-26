from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import sqlite3

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DB_PATH = "message_map.db"


def init_db():
    """Создаёт таблицу для хранения связей сообщений и пользователей."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS message_map (
                admin_message_id INTEGER PRIMARY KEY,
                user_id          INTEGER NOT NULL
            )
        """)


def save_mapping(admin_message_id: int, user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO message_map VALUES (?, ?)",
            (admin_message_id, user_id)
        )


def get_user_id(admin_message_id: int) -> int | None:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT user_id FROM message_map WHERE admin_message_id = ?",
            (admin_message_id,)
        ).fetchone()
    return row[0] if row else None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start."""
    await update.message.reply_text(
        "Приветствую! Напишите Ваше сообщение (заявку), и я передам администратору."
    )


async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает сообщение пользователя админу."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name
    user_message = update.message.text

    message_to_admin = f"Сообщение от {user_name} (ID: {user_id}):\n{user_message}"
    sent = await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)
    save_mapping(sent.message_id, user_id)


async def handle_admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответы администратора и пересылает их пользователю."""
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Ответьте на сообщение пользователя, чтобы отправить ответ."
        )
        return

    admin_reply_id = update.message.reply_to_message.message_id
    user_id = get_user_id(admin_reply_id)

    if user_id:
        await context.bot.send_message(chat_id=user_id, text=update.message.text)
        await update.message.reply_text("Ответ успешно отправлен пользователю.")
    else:
        await update.message.reply_text(
            "Не удалось найти пользователя для этого сообщения."
        )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан")
    if not ADMIN_ID:
        raise RuntimeError("ADMIN_ID не задан")

    init_db()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Сообщения от обычных пользователей (не от админа)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT
        & ~filters.Chat(ADMIN_ID)
        & ~filters.FORWARDED
        & ~filters.UpdateType.EDITED,
        forward_to_admin
    ))

    # Ответы от админа
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Chat(ADMIN_ID),
        handle_admin_response
    ))

    application.run_polling()


if __name__ == "__main__":
    main()
