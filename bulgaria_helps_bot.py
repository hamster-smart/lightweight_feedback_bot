from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
BOT_TOKEN = "7878432935:AAHVwLQ8E79f2f5fN4M_s3CdK-6Eh5Attrc"

# Flask приложение для фиктивного порта и Webhook
app = Flask(__name__)

# Переменные окружения
BOT_TOKEN = os.getenv("7878432935:AAHVwLQ8E79f2f5fN4M_s3CdK-6Eh5Attrc")
WEBHOOK_URL = f"https://telegram-feedback-bot-pw8r.onrender.com/webhook"  # Замените на URL вашего сервиса
ADMIN_ID = 5240690995  # Вставьте свой Telegram ID

# Создаем экземпляр приложения Telegram
application = ApplicationBuilder().token(BOT_TOKEN).build()

@app.route('/')
def index():
    return "Bot is running through Webhook!"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Получение обновлений от Telegram через Webhook."""
    json_update = request.get_json()
    update = Update.de_json(json_update, application.bot)
    application.update_queue.put_nowait(update)
    return "OK"

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
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.FORWARDED) & (~filters.UpdateType.EDITED), forward_to_admin))

    # Обработка сообщений от админа
    if ADMIN_ID:
        application.add_handler(MessageHandler(filters.TEXT & filters.Chat(ADMIN_ID), handle_admin_response))

    # Устанавливаем Webhook для бота
    application.bot.set_webhook(WEBHOOK_URL)

    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))

if __name__ == '__main__':
    main()
