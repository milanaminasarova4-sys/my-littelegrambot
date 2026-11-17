import requests
import telebot
from telebot import types

# --- НАСТРОЙКИ БОТА ---
TOKEN = "8887827299:AAF4aGlFLAbP2wu33T8Xvy3BRWu3Nh8Enmc"
MY_ID = 89034144442 # Замените на ваш реальный Telegram ID для получения заявок

# --- НАСТРОЙКИ YANDEX CLOUD (YandexGPT) ---
FOLDER_ID = "b1g6jafvag1lkt768hij"
YANDEX_API_KEY = "AQVNzcHDuHVq0Z3cNPNTvscGFxk5ot2vDjDUd5Ma"

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()


# --- ФУНКЦИЯ ПОДКЛЮЧЕНИЯ К ИИ YANDEX CLOUD ---
def ask_yandex_gpt(user_message):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}"
    }

    system_prompt = (
        "Ты вежливый и бережный ИИ-помощник клиники и центра психологии. "
        "Твоя задача — выслушать человека, поддержать его и подсказать, к какому специалисту лучше записаться "
        "(к терапевту, психологу или семейному психологу). "
        "Не ставь медицинских диагнозов и не назначай лекарства. "
        "Отвечай тепло, кратко и по делу. Напоминай, что оформить запись можно через кнопку «📅 Записаться на приём»."
    )

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.5,
            "maxTokens": 500
        },
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": user_message}
        ]
    }

    response = requests.post(url, headers=headers, json=data, timeout=15)
    response.raise_for_status()
    result = response.json()
    return result["result"]["alternatives"][0]["message"]["text"]


# --- ГЛАВНОЕ МЕНЮ ---
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_about = types.KeyboardButton("🩺 О специалистах")
    btn_prices = types.KeyboardButton("💳 Услуги и стоимость")
    btn_location = types.KeyboardButton("📍 Адрес и часы работы")
    btn_book = types.KeyboardButton("📅 Записаться на приём")
    btn_ai = types.KeyboardButton("🧠 Помощь ИИ-ассистента")
    markup.add(btn_about, btn_prices)
    markup.add(btn_location, btn_book)
    markup.add(btn_ai)
    return markup


# --- Команда /start: Приветствие ---
@bot.message_handler(commands=["start"])
def welcome(message):
    welcome_text = (
        f"👋 Здравствуйте, {message.from_user.first_name}!\n\n"
        "Добро пожаловать в бот записи к **терапевту и психологу**. 🩺🌿\n"
        "Здесь вы можете узнать о специалистах, посмотреть стоимость приёма, выбрать удобное время для записи или задать вопрос нашему ИИ-помощнику.\n\n"
        "💡 *Подсказка:* нажмите /ai, чтобы проверить статус подключения ИИ через Yandex Cloud."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")


# --- Команда /ai: Проверка подключения ИИ через Yandex Cloud ---
@bot.message_handler(commands=["ai"])
def check_ai_status(message):
    bot.send_chat_action(message.chat.id, "typing")
    try:
        # Проверяем реальное соединение с Yandex Cloud
        test_reply = ask_yandex_gpt("Привет! Подтверди одним коротким предложением, что ты на связи и готов помочь с выбором врача или психолога.")
        status_text = (
            "✅ **ИИ успешно подключён через Yandex Cloud!**\n"
            "• Платформа: Yandex Foundation Models (YandexGPT)\n"
            f"• Каталог (Folder ID): `{FOLDER_ID[:6]}***`\n\n"
            f"💬 *Ответ ИИ:* {test_reply}\n\n"
            "Просто напишите сюда свой вопрос или опишите, что вас беспокоит."
        )
        bot.send_message(message.chat.id, status_text, parse_mode="Markdown")
    except Exception as e:
        error_text = (
            "❌ **Ошибка подключения к Yandex Cloud.**\n"
            "Проверьте правильность `FOLDER_ID` и `YANDEX_API_KEY` в настройках кода.\n\n"
            f"Техническая деталь: `{e}`"
        )
        bot.send_message(message.chat.id, error_text, parse_mode="Markdown")


# --- Обработка кнопок меню и свободных сообщений ---
@bot.message_handler(content_types=["text"])
def handle_buttons(message):
    if message.text == "🩺 О специалистах":
        about_text = (
            "🩺 *Наши специалисты*\n\n"
            "• **Врач-терапевт** — первичный осмотр, диагностика, составление плана обследования и лечения, расшифровка анализов.\n"
            "• **Клинический психолог** — индивидуальные консультации, работа со стрессом, тревогой, выгоранием и сложными жизненными ситуациями.\n\n"
            "🤝 *Наш подход:* внимательное отношение, конфиденциальность и доказательная медицина."
        )
        bot.send_message(message.chat.id, about_text, parse_mode="Markdown")

    elif message.text == "💳 Услуги и стоимость":
        prices_text = (
            "💳 *Услуги и стоимость приёма*\n\n"
            "• Первичный приём врача-терапевта — 2 500 ₽\n"
            "• Повторный приём терапевта — 2 000 ₽\n"
            "• Индивидуальная консультация психолога — 3 500 ₽\n"
            "• Семейная консультация психолога — 5 000 ₽\n\n"
            "⏳ *Длительность приёма:* терапевт — 30–40 минут, психолог — 55 минут."
        )
        bot.send_message(message.chat.id, prices_text, parse_mode="Markdown")

    elif message.text == "📍 Адрес и часы работы":
        location_text = (
            "📍 *Адрес центра*\n"
            "ул. Примерная, д. 15, офис 204 (вход со стороны сквера)\n\n"
            "🕒 *Часы работы*\n"
            "• Понедельник – Пятница: 08:30 – 20:00\n"
            "• Суббота: 09:00 – 17:00\n"
            "• Воскресенье: Выходной\n\n"
            "📞 *Телефон регистратуры:* +7 (999) 123-45-67"
        )
        bot.send_message(message.chat.id, location_text, parse_mode="Markdown")

    elif message.text == "🧠 Помощь ИИ-ассистента":
        bot.send_message(
            message.chat.id,
            "🧠 ИИ-помощник (Yandex Cloud) на связи!\n\n"
            "Напишите в свободной форме, что вас беспокоит или какой вопрос возник — я помогу определиться, к какому специалисту лучше записаться."
        )

    # --- НАЧАЛО ПРОЦЕССА ЗАПИСИ ---
    elif message.text == "📅 Записаться на приём":
        markup_services = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_1 = types.KeyboardButton("Приём терапевта")
        btn_2 = types.KeyboardButton("Консультация психолога")
        btn_3 = types.KeyboardButton("Семейный психолог")
        btn_4 = types.KeyboardButton("Онлайн-консультация")
        markup_services.add(btn_1, btn_2)
        markup_services.add(btn_3, btn_4)

        msg = bot.send_message(
            message.chat.id,
            "Шаг 1/3: К какому специалисту вы хотите записаться?",
            reply_markup=markup_services,
        )
        bot.register_next_step_handler(msg, process_service_step)

    # --- ЛЮБОЙ ДРУГОЙ ТЕКСТ -> ОБРАБАТЫВАЕТ ИИ YANDEX CLOUD ---
    else:
        bot.send_chat_action(message.chat.id, "typing")
        try:
            ai_reply = ask_yandex_gpt(message.text)
            bot.send_message(message.chat.id, ai_reply)
        except Exception as e:
            print(f"Ошибка YandexGPT: {e}")
            bot.send_message(
                message.chat.id,
                "Сейчас ИИ-помощник временно недоступен, но вы можете записаться на приём через кнопку «📅 Записаться на приём» ниже."
            )


# --- Шаг 3: Выбор специалиста -> Запрос даты и времени ---
def process_service_step(message):
    service = message.text

    if service == "/start":
        welcome(message)
        return

    markup_time = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_today = types.KeyboardButton("Сегодня (ближайшее окно)")
    btn_tomorrow_morning = types.KeyboardButton("Завтра в первой половине дня")
    btn_tomorrow_evening = types.KeyboardButton("Завтра во второй половине дня")
    markup_time.add(btn_today)
    markup_time.add(btn_tomorrow_morning, btn_tomorrow_evening)

    msg = bot.send_message(
        message.chat.id,
        f"Вы выбрали: *{service}*\n\nШаг 2/3: Выберите удобное время или напишите свой вариант (например, «В среду после 17:00»):",
        reply_markup=markup_time,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_time_step, service)


# --- Шаг 4: Выбор времени -> Запрос номера телефона ---
def process_time_step(message, service):
    booking_time = message.text

    if booking_time == "/start":
        welcome(message)
        return

    markup_phone = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_phone = types.KeyboardButton("📱 Отправить мой номер телефона", request_contact=True)
    markup_phone.add(btn_phone)

    msg = bot.send_message(
        message.chat.id,
        "Шаг 3/3: Нажмите кнопку ниже, чтобы передать номер телефона — администратор свяжется с вами и подтвердит запись:",
        reply_markup=markup_phone
    )
    bot.register_next_step_handler(msg, process_final_step, service, booking_time)


# --- Шаг 5: Финал -> Подтверждение пациенту и уведомление врачу/админу ---
def process_final_step(message, service, booking_time):
    if message.contact:
        phone_number = message.contact.phone_number
    else:
        phone_number = message.text

    if phone_number == "/start":
        welcome(message)
        return

    bot.send_message(
        message.chat.id,
        "✅ *Заявка принята!* Спасибо за обращение. Мы свяжемся с вами в ближайшее время для подтверждения времени приёма.",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

    username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"
    client_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()

    notification_text = (
        f"🩺 📋 **НОВАЯ ЗАПИСЬ НА ПРИЁМ!**\n\n"
        f"👤 *Пациент:* {client_name}\n"
        f"📱 *Telegram:* {username}\n"
        f"📞 *Телефон:* {phone_number}\n\n"
        f"👨‍⚕️ *Специалист:* {service}\n"
    )
bot.polling(none_stop=True)