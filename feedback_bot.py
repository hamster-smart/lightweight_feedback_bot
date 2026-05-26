import telebot
from telebot import types
import os
from dotenv import load_dotenv
import security

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_ID")

if not API_TOKEN or not ADMIN_CHAT_ID:
    print("Ошибка: переменные окружения не загружены. Проверьте .env или environment в docker-compose.")
    print(f"API_TOKEN: {'OK' if API_TOKEN else 'MISSING'}, ADMIN_ID: {'OK' if ADMIN_CHAT_ID else 'MISSING'}")
    exit(1)

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
def handle_start_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Связаться с администратором"))
    bot.send_message(
        message.chat.id,
        "Приветствую! Напишите Ваше сообщение (заявку), и я передам администратору.",
        reply_markup=markup,
    )


@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    # Сообщения от самого админа не пересылаем
    if str(message.chat.id) == str(ADMIN_CHAT_ID):
        return

    if not security.is_user_request_allowed(message.chat.id):
        bot.send_message(
            message.chat.id,
            "Вы отправляете сообщения слишком часто. Подождите немного.",
        )
        return

    if not security.is_valid_message(message.text):
        bot.send_message(
            message.chat.id,
            "Ваше сообщение содержит недопустимые ссылки. Попробуйте без них.",
        )
        return

    if message.text.startswith("/"):
        bot.send_message(message.chat.id, "Неизвестная команда. Попробуйте снова.")
        return

    if message.text == "Связаться с администратором":
        bot.send_message(message.chat.id, "Пожалуйста, опишите вашу проблему:")
        return

    user_id = message.chat.id
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "Ответить",
            callback_data=f"reply:{user_id}:{message.message_id}",
        )
    )

    bot.send_message(
        ADMIN_CHAT_ID,
        f"Сообщение от {full_name} (ID: {user_id}):\n{message.text}",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("reply:"))
def handle_reply_button(call):
    try:
        _, user_id, _ = call.data.split(":")
        bot.answer_callback_query(call.id)
        sent = bot.send_message(ADMIN_CHAT_ID, f"Введите ответ для пользователя {user_id}:")
        bot.register_next_step_handler(sent, send_reply, user_id)
    except Exception as e:
        bot.send_message(ADMIN_CHAT_ID, f"Ошибка при обработке кнопки: {e}")


def send_reply(message, user_id):
    try:
        bot.send_message(user_id, message.text)
        bot.send_message(ADMIN_CHAT_ID, f"Ответ отправлен пользователю {user_id}.")
    except Exception as e:
        bot.send_message(ADMIN_CHAT_ID, f"Не удалось отправить ответ: {e}")


bot.infinity_polling()
