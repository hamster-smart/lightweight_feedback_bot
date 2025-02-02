from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import http.server
import socketserver
import threading

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Используем переменную окружения для токена
ADMIN_ID = 5240690995  # Вставьте свой Telegram ID

# Словарь для хранения связей сообщений и пользователей
user_message_map = {}

# Создаем экземпляр приложения Telegram
application = ApplicationBuilder().token(BOT_TOKEN).build()

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

    # Сохраняем связь сообщения и user_id
    sent_message = await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)
    user_message_map[sent_message.message_id] = user_id  # Привязываем message_id к user_id

async def handle_admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответы администратора и пересылает их пользователю."""
    if update.message.reply_to_message:
        # Получаем ID пользователя из словаря
        admin_reply_id = update.message.reply_to_message.message_id
        user_id = user_message_map.get(admin_reply_id)

        if user_id:
            # Отправляем ответ пользователю
            await context.bot.send_message(chat_id=user_id, text=update.message.text)
            await update.message.reply_text("Ответ успешно отправлен пользователю.")
        else:
            await update.message.reply_text("Не удалось найти пользователя для этого сообщения.")
    else:
        await update.message.reply_text("Ответьте на сообщение пользователя, чтобы отправить ответ.")

def run_server():
    """Фиктивный HTTP-сервер для Render."""
    PORT = int(os.getenv("PORT", 8080))

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot is running!")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

def main():
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.FORWARDED) & (~filters.UpdateType.EDITED), forward_to_admin))

    # Обработка сообщений от админа
    if ADMIN_ID:
        application.add_handler(MessageHandler(filters.TEXT & filters.Chat(ADMIN_ID), handle_admin_response))

    # Запускаем фиктивный сервер параллельно с ботом
    threading.Thread(target=run_server, daemon=True).start()

    # Запускаем бота с использованием long polling
    application.run_polling()

if __name__ == '__main__':
    main()
