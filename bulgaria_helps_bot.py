from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

ADMIN_ID = 5240690995  # Замените на свой Telegram ID
BOT_TOKEN = "7878432935:AAGgCShIs7jl9AYLe1KR1Nik5_2FKU93lP4"  # Вставьте свой токен

async def start(update: Update, context):
    """Команда /start."""
    await update.message.reply_text("Приветствую! Напишите сообщение (заявку), и я передам его администратору.")

async def forward_to_admin(update: Update, context):
    """Пересылает сообщение пользователя админу."""
    user_message = update.message.text
    user_name = update.message.from_user.full_name
    user_id = update.message.from_user.id

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Сообщение от {user_name} (ID: {user_id}):\n{user_message}"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, forward_to_admin))

    app.run_polling()

if __name__ == '__main__':
    main()
