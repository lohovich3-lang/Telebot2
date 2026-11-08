import os
import random
import threading
import time
import telebot
from flask import Flask
from telebot import types

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask("")

@app.route("/")
def home():
    return "Бот успешно работает 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

n1 = ["админ гей", "админ лох", "админ лошара", "админ даун"]
n2 = ["поддержать", "донат", "пожертв"]
n3 = [
    "пидор", "хуесос", "гнида", 
    "далбаеб", "долбаеб", "петух", "уеб", "уёб", "ганд", 
    "гонд", "пидр",
]
n4 = [
    "всем привет", "всем здарова", "всем салам", "здрасте", 
    "здрасьте", "здравствуйте", "привет парни", "пацаны привет", 
    "привет пацаны"
]
n5 = [
    "люблю", "любил", "влюблил", "влюблен", "свидани", 
    "романтик", "привязанность", "привязал", "нежность", 
    "страсть", "поцелу", "любов"
]
n6 = [
    "@ttteto_bot кто @"
]
ADMIN_ID = 1475257511

user_last_message_time = {}
SPAM_INTERVAL = 2  # Интервал антиспама в секундах

DB_FILE = "numbers_list.txt"

commands_list = [
    types.BotCommand("pravila", "Показать правила чата"),
    types.BotCommand("what", "Что делает бот на то или иное слово"),
]

bot.set_my_commands(commands_list)


# --- Функции для работы с числами ---
def load_numbers():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                numbers = []
                for line in lines:
                    val = line.strip()
                    if val:
                        num = float(val) if "." in val else int(val)
                        numbers.append(num)
                return numbers
        except Exception:
            pass
    return []


def save_number(number, append=True):
    mode = "a" if append else "w"
    with open(DB_FILE, mode, encoding="utf-8") as f:
        f.write(f"{number}\n")


# --- Исправленная логика удаления сообщений ---
def delete_message_later(chat_id, message_id, delay=300):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Не удалось удалить сообщение {message_id}: {e}")


def schedule_deletion(*messages, delay=300):
    """Принимает объекты сообщений и запускает их отложенное удаление в фоновом потоке."""
    for msg in messages:
        if msg:  # Проверяем, что сообщение успешно создано/существует
            threading.Thread(
                target=delete_message_later,
                args=(msg.chat.id, msg.message_id, delay),
            ).start()


@bot.message_handler(commands=["pravila", "Правила"])
def send_welcome(message):
    sent_msg = bot.reply_to(
        message,
        "Приветствую!\nНынешние правила:\n1) Запрещены любые оскорбления (кроме"
        " в сторону админа)\n2) Запрещена любая рекламная хуйня и т.д.\n3) Больше"
        " не придумал:(",
    )
    # Удаляем триггер пользователя и ответ бота через 5 минут
    schedule_deletion(message, sent_msg, delay=300)

@bot.message_handler(commands=["what", "ЧеПоЧем"])
def send_welcome(message):
    sent_msg = bot.reply_to(
        message,
        "На что бот гавкает?\n" \
        "Срабатывает при определенных условиях(хз каких) 👇👇\n" \
        "1. Котик\n" \
        "2. Приветствие\n" \
        "4. Донат и ему синоним\n" \
        "3. Дальше секрет т.к. будете как-либо это использовать\n"
        "Нахуя я вообще пишу о трех функциях?"
    )
    schedule_deletion(message, sent_msg, delay=300)


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if not message.text:
        return

    text = message.text.lower()
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_time = time.time()

    # --- 1. ЗАЩИТА ОТ СПАМА ДЛЯ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ ---
    if user_id != ADMIN_ID:
        if user_id in user_last_message_time:
            time_diff = current_time - user_last_message_time[user_id]
            if time_diff < SPAM_INTERVAL:
                try:
                    # Удаляем сообщение спамера мгновенно
                    bot.delete_message(chat_id, message.message_id)
                    return
                except Exception as e:
                    print(f"Не удалось удалить спам: {e}")
        user_last_message_time[user_id] = current_time
    # ----------------------------------------------------

    # --- 2. ЛОГИКА ДЛЯ АДМИНИСТРАТОРА ---
    if user_id == ADMIN_ID:
        # Обработка команды /set (только для админа)
        if text.startswith("/set"):
            command_parts = message.text.split(maxsplit=1)
            if len(command_parts) < 2:
                sent_msg = bot.reply_to(
                    message,
                    "⚠️ Укажите число.\n**Пример:** `/set 100`",
                    parse_mode="Markdown",
                )
            else:
                try:
                    val = command_parts[1].replace(",", ".")
                    num = float(val)
                    if num.is_integer():
                        num = int(num)
                    save_number(num, append=False)
                    sent_msg = bot.reply_to(
                        message,
                        f"🔄 Список очищен. Первый донат **{num}** сохранен!",
                        parse_mode="Markdown",
                    )
                except ValueError:
                    sent_msg = bot.reply_to(
                        message, "⚠️ Ошибка! Введите корректное число."
                    )
            schedule_deletion(message, sent_msg, delay=600)
            return
        
        # Обработка команды /add (только для админа)
        elif text.startswith("/add"):
            command_parts = message.text.split(maxsplit=1)
            if len(command_parts) < 2:
                sent_msg = bot.reply_to(
                    message,
                    "⚠️ Укажите донат для добавления.\n**Пример:** `/add 50`",
                    parse_mode="Markdown",
                )
            else:
                try:
                    val = command_parts[1].replace(",", ".")
                    new_num = float(val)
                    if new_num.is_integer():
                        new_num = int(new_num)

                    save_number(new_num, append=True)
                    numbers = load_numbers()
                    total = sum(numbers)
                    if isinstance(total, float) and total.is_integer():
                        total = int(total)

                    column_str = "\n".join(str(n) for n in numbers)
                    response = (
                        f"📥 **Все сохраненные пожертвования:**\n\n"
                        f"{column_str}\n"
                        f"────────\n"
                        f"**Сумма: {total}**"
                    )
                    sent_msg = bot.reply_to(message, response, parse_mode="Markdown")
                except ValueError:
                    sent_msg = bot.reply_to(
                        message, "⚠️ Ошибка! Введите корректное число."
                    )
            schedule_deletion(message, sent_msg, delay=600)
            return

        # Старые админские команды
        elif text == "привет, идиот.":
            sent_msg = bot.reply_to(message, "Привет @Nikita2015PRO, Как дела?")
            schedule_deletion(message, sent_msg, delay=600)
        elif text == "все супер,как сам?.":
            sent_msg = bot.reply_to(
                message,
                "Прекрасно, работаю за бесплатно.\nПоэтому, будь добр, не отвлекай"
                " меня от работы...",
            )
            schedule_deletion(message, sent_msg, delay=600)
        elif text == "извини((.":
            sent_msg = bot.reply_to(message, "...")
            schedule_deletion(message, sent_msg, delay=600)
        elif text == "goodboy":
            sent_msg = bot.reply_to(message, "Woaf woaf!")
            schedule_deletion(message, sent_msg, delay=200)
        else:
            pass

    # --- 3. ЛОГИКА ДЛЯ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ ---
    else:
        # Если обычный пользователь попытается написать /set или /add, бот проигнорирует их
        if text.startswith("/set") or text.startswith("/add"):
            return

        # Проверка n1 (Гифка-детектор)
        if any(word in text for word in n1):
            gif_url = "https://tenor.com"
            sent_msg = bot.send_animation(
                chat_id=message.chat.id,
                animation=gif_url,
                caption="🫣",
                reply_to_message_id=message.message_id,
            )
            schedule_deletion(message, sent_msg, delay=600)

        # Проверка n2 (Донат)
        elif any(word in text for word in n2):
            sent_msg = bot.reply_to(
                message,
                "Ссылка на пожертвование - https://dalink.to\nСпасибо <3",
            )
            schedule_deletion(message, sent_msg, delay=600)

        # Проверка n3 (Оскорбления / вызов админа)
        elif any(word in text for word in n3):
            sent_msg = bot.reply_to(
                message,
                "@Nikita2015PRO , у нас тут придурок объявился!\nВозможна ошибка,"
                " заранее извиняюсь!",
            )
            schedule_deletion(message, sent_msg, delay=600)

        # Проверка "котик"
        elif text == "котик":
            variant = [
                "https://media.tenor.com/lfDATg4Bhc0AAAAM/happy-cat.gif",
                "https://media.tenor.com/l8lnhRNnlMwAAAAM/cat-cat-meme.gif",
                "https://media.tenor.com/cRTQk6N_FxMAAAAM/swag-cat-swagbilli-cutecat-cats-cat-swag-ok-yooo-yo.gif",
                "https://media.tenor.com/OOj-QK2NxUkAAAAM/cat-kitty.gif",
                "https://media.tenor.com/QSEW0tZz4OUAAAAM/cat.gif",
                "https://media.tenor.com/FWYFkElU8UIAAAAM/7tv-cat-meme.gif",
                "https://media.tenor.com/TqNG5XNntroAAAAM/so-tuff.gif",
                "https://media.tenor.com/WVTEnkzM9_UAAAAM/cat-cat-smile.gif",
                "https://media.tenor.com/omBQ2kB8A_oAAAAM/kattus-ultrus-fetus.gif",
                "https://media.tenor.com/onFHdpJsiKUAAAAm/zazu-burger.webp",
                "https://media.tenor.com/t8RTOfWcIYUAAAAM/appetite-hungry.gif",
                "https://media.tenor.com/kKeM0-othPUAAAAm/fat-long-cat.webp",
                "https://media.tenor.com/pdX9YTI4_eoAAAA1/cat-cat-with-tongue.webp",
                "https://media.tenor.com/wcDBzYCQyOgAAAAM/ice-cream-cat.gif",
                "https://media.tenor.com/298Aly2LzQwAAAAM/smiling-cat-happy-cat.gif",
                "https://media.tenor.com/tNr8zcDCyoYAAAAM/cat.webp",
            ]
            sent_msg = bot.reply_to(message, random.choice(variant))
            schedule_deletion(message, sent_msg, delay=600)

        # Проверка n4 (Приветствия)
        elif any(word in text for word in n4):
            sent_msg = bot.reply_to(message, "Привет!")
            schedule_deletion(message, sent_msg, delay=600)
    
        # Проверка n5 (Романтика)
        elif any(word in text for word in n5):
            sent_msg = bot.reply_to(
                message, 
                "Фу,пошел нахуй романтик ебучий \n woaf woaf",
            )
            schedule_deletion(message, sent_msg, delay=600)

        elif text == "@ttteto_bot кто @Sigmartyomchik ?":
            variant2 = [
                "лох", "гей", "лошара", "лошпед", "онанист", "придурок", "дурак😒"
            ]
            sent_msg = bot.reply_to(message, random.choice(variant2))
            schedule_deletion(message, sent_msg, delay=600)




if __name__ == "__main__":
    # keep_alive() # Раскомментируйте, если запускаете на Replit/Render
    print("Идиот вышел на работу...")
    bot.infinity_polling()
