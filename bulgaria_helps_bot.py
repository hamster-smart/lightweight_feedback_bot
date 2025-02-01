from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import os

# Создаем Flask приложение для фиктивного ожидания порта
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# ID администратора (замените на ваш)
ADMIN_ID = 5240690995  # Вставьте свой Telegram ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start."""
    await update.message.reply_text("Приветствую! Напишите Ваше сообщение (заявку), и я передам администратору.")

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пересылает сообщение пользователя админу."""
    user_message = update.message.text
    user_id = update.message.from_user.id
    user_name = update.message.from_user.full_name

    # Формируем сообщение для администратора
    message_to_admin = f"Сообщение от {user_name} (ID: {user_id}):\n{user_message}"

    # Пересылаем сообщение админу
    await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)

async def handle_admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответы администратора и пересылает их пользователю."""
    if update.message.reply_to_message:
        # Получаем ID пользователя из текста ответа
        text = update.message.reply_to_message.text
        user_id_start = text.find("ID: ") + 4
        user_id_end = text.find(")", user_id_start)
        user_id = int(text[user_id_start:user_id_end])

        # Отправляем ответ пользователю
        await context.bot.send_message(chat_id=user_id, text=update.message.text)
    else:
        await update.message.reply_text("Ответьте на сообщение пользователя, чтобы отправить ответ.")

def main():
    # Вставьте свой токен бота
    TOKEN = "7878432935:AAGgCShIs7jl9AYLe1KR1Nik5_2FKU93lP4"
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.FORWARDED) & (~filters.UpdateType.EDITED), forward_to_admin))

    # Обработка сообщений от админа
    if ADMIN_ID:
        application.add_handler(MessageHandler(filters.TEXT & filters.Chat(ADMIN_ID), handle_admin_response))

    # Запускаем бота
    application.run_polling()

    # Запуск Flask для фиктивного ожидания порта
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))

if __name__ == '__main__':
    main()
