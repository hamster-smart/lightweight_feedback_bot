from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import http.server
import socketserver
import threading

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Используем переменную окружения для токена
ADMIN_ID = 5240690995  # Вставьте свой Telegram ID

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

    # Пересылаем сообщение админу
    await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)

async def handle_admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответы администратора и пересылает их пользователю."""
    if update.message.reply_to_message:
        # Получаем ID пользователя из оригинального сообщения
        original_message = update.message.reply_to_message.text
        user_id_start = original_message.find("ID: ") + 4
        user_id_end = original_message.find(")", user_id_start)

        if user_id_start != -1 and user_id_end != -1:
            try:
                user_id = int(original_message[user_id_start:user_id_end])

                # Отправляем ответ пользователю
                await context.bot.send_message(chat_id=user_id, text=update.message.text)
                await update.message.reply_text("Ответ успешно отправлен пользователю.")
            except ValueError:
                await update.message.reply_text("Ошибка извлечения ID пользователя.")
        else:
            await update.message.reply_text("Не найден ID пользователя для ответа.")
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
