import time
import re

# In-memory rate limiting — resets on restart, acceptable for this use case
user_message_times: dict[int, float] = {}


def is_user_request_allowed(user_id: int, cooldown_period: int = 10) -> bool:
    """Returns False if the user sent a message less than cooldown_period seconds ago."""
    current_time = time.time()
    last = user_message_times.get(user_id)
    if last and current_time - last < cooldown_period:
        return False
    user_message_times[user_id] = current_time
    return True


def is_valid_message(message_text: str) -> bool:
    """Rejects messages containing http/https links."""
    return not re.search(r"https?://[^\s]+", message_text)


def handle_error(bot, admin_chat_id: str, error: Exception, update=None):
    """Notifies admin about an error and optionally informs the user."""
    try:
        bot.send_message(admin_chat_id, f"Ошибка: {error}")
    except Exception as e:
        print(f"Не удалось уведомить админа: {e}")

    try:
        if update and hasattr(update, "message") and update.message:
            bot.send_message(update.message.chat.id, "Произошла ошибка, попробуйте ещё раз.")
    except Exception as e:
        print(f"Не удалось уведомить пользователя: {e}")
