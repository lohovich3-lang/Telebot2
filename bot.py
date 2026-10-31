import os
import random
import threading
import time
import telebot
from flask import Flask

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


app = Flask("")

@app.route("/")
def home():
  return "Бот успешно работает 24\7!"

def run_flask():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)

def keep_alive():
  t = threading.Thread(target=run_flask)
  t.start()






n1 = ["админ гей", "админ лох", "админ лошара", "админ даун"]
n2 = ["поддержать", "донат", "пожертв"]
n3 = [
    "ебал",
    "пидор",
    "хуесос",
    "бляд",
    "гнида",
    "далбаеб",
    "долбаеб",
    "петух",
    "уеб",
    "уёб",
    "ганд",
    "гонд",
    "пидр",
    "ебан",
]
n4 = [
    "всем привет",
    "всем здарова",
    "всем салам",
    "здрасте",
    "здрасьте",
    "здравствуйте",
    "привет парни",
    "пацаны привет",
    "привет пацаны",
]
ADMIN_ID = 1475257511

user_last_message_time = {}
SPAM_INTERVAL = 1.5  # Интервал антиспама в секундах


# Функция для отложенного удаления сообщений (300 секунд = 5 минут)
def delete_message_later(chat_id, message_id, delay=300):
  time.sleep(delay)
  try:
    bot.delete_message(chat_id, message_id)
  except Exception as e:
    print(f"Не удалось удалить сообщение! {e}")


# Вспомогательная функция для быстрой отправки и настройки удаления через 5 минут
def send_and_schedule_deletion(chat_id, message_id, sent_message):
  threading.Thread(
      target=delete_message_later,
      args=(sent_message.chat.id, sent_message.message_id, 300),
  ).start()


@bot.message_handler(commands=["pravila", "Правила"])
def send_welcome(message):
  sent_msg = bot.reply_to(
      message,
      "Приветствую!\nНынешние правила:\n1) Запрещены любые оскорбления (кроме"
      " в сторону админа)\n2) Запрещена любая рекламная хуйня и т.д.\n3) Больше"
      " не придумал:(",
  )
  send_and_schedule_deletion(message.chat.id, message.message_id, sent_msg)


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
    if text == "привет, идиот.":
      sent_msg = bot.reply_to(message, "Привет @Nikita2015PRO, Как дела?")
      send_and_schedule_deletion(chat_id, message.message_id, sent_msg)
    elif text == "все супер,как сам?.":
      sent_msg = bot.reply_to(
          message,
          "Прекрасно, работаю за бесплатно.\nПоэтому, будь добр, не отвлекай"
          " меня от работы...",
      )
      send_and_schedule_deletion(chat_id, message.message_id, sent_msg)
    elif text == "извини((.":
      sent_msg = bot.reply_to(message, "...")
      send_and_schedule_deletion(chat_id, message.message_id, sent_msg)
    else:
      pass

  # --- 3. ЛОГИКА ДЛЯ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ ---
  else:
    # Проверка n1 (Гифка-детектор)
    if any(word in text for word in n1):
      gif_url = "https://media1.giphy.com/media/3o7TKSjRrfIPjeiOkM/giphy.gif"
      sent_msg = bot.send_animation(
          chat_id=message.chat.id,
          animation=gif_url,
          caption="🫣",
          reply_to_message_id=message.message_id,
      )
      send_and_schedule_deletion(chat_id, message.message_id, sent_msg)

    # Проверка n2 (Донат)
    elif any(word in text for word in n2):
      sent_msg = bot.reply_to(
          message,
          "Ссылка на пожертвование - https://dalink.to/rnghuman\nСпасибо <3",
      )
      send_and_schedule_deletion(chat_id, message.message_id, sent_msg)

    # Проверка n3 (Оскорбления / вызов админа)
    elif any(word in text for word in n3):
      sent_msg = bot.reply_to(
          message,
          "@Nikita2015PRO , у нас тут придурок объявился!\nВозможна ошибка,"
          " заранее извиняюсь!",
      )
      send_and_schedule_deletion(chat_id, message.message_id, sent_msg)

    # Проверка "котик"
    elif text == "котик":
      variant = [
          "https://media.tenor.com/lfDATg4Bhc0AAAAM/happy-cat.gif",
          "https://media.tenor.com/l8lnhRNnlMwAAAAM/cat-cat-meme.gif",
          (
              "https://media.tenor.com/cRTQk6N_FxMAAAAM/swag-cat-swagbilli-cutecat-cats-cat-swag-ok-yooo-yo.gif"
          ),
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
      send_and_schedule_deletion(chat_id, message.message_id, sent_msg)

    # Проверка n4 (Приветствия)
    elif any(word in text for word in n4):
      sent_msg = bot.reply_to(message, "Привет!")
      send_and_schedule_deletion(chat_id, message.message_id, sent_msg)


if __name__ == "__main__":
  print("Идиот вышел на работу...")
  bot.infinity_polling()
