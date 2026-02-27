import requests
import os
from datetime import datetime

# Налаштування (беруться зі змінних середовища GitHub)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Kyiv"  # Можеш змінити на своє місто

def get_data(url):
    """Отримує текстові дані з GitHub"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Помилка завантаження {url}: {e}")
        return None

def get_file_info(file_name, search_key):
    """Шукає рядок за ключем MM-DD у файлах names.txt та history.txt"""
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    data = get_data(url)
    if data:
        for line in data.splitlines():
            if line.startswith(search_key):
                # Відрізаємо дату (напр. "02-27 ") і повертаємо текст
                return line[6:].strip()
    return None

def get_weather():
    """Отримує погоду через OpenWeatherMap"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url).json()
        temp = round(res["main"]["temp"])
        desc = res["weather"][0].capitalize()
        return f"{temp}°C, {desc}"
    except:
        return "не вдалося отримати"

def get_currency():
    """Отримує курс валют НБУ"""
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    try:
        res = requests.get(url).json()
        usd = next(item for item in res if item["cc"] == "USD")["rate"]
        eur = next(item for item in res if item["cc"] == "EUR")["rate"]
        return f"🇺🇸 USD: {usd:.2f} | 🇪🇺 EUR: {eur:.2f}"
    except:
        return "курси тимчасово недоступні"

def send_message():
    """Формує та надсилає повідомлення в Telegram"""
    now = datetime.now()
    date_key = now.strftime("%m-%d")
    date_display = now.strftime("%d.%m.%Y")

    # Отримуємо дані з файлів
    names_list = get_file_info("names.txt", date_key)
    history_note = get_file_info("history.txt", date_key)
    weather = get_weather()
    currency = get_currency()

    # Секція іменин з твоїми побажаннями
    if names_list:
        names_text = (
            f"😇 **В цей день свої іменини святкують:**\n{names_list}\n\n"
            f"✨ _Не забудь привітати близьких, якщо серед твого оточення є люди з такими іменами. Їм буде приємно!_"
        )
    else:
        names_text = "😇 **Сьогодні іменини не вказані.**"

    # Секція історії
    history_text = f"🕰 **Цей день в історії:**\n{history_note if history_note else 'Цікавих подій не знайдено.'}"

    # Формуємо фінальний текст
    full_message = (
        f"📅 **Сьогодні {date_display}**\n\n"
        f"--- \n"
        f"{names_text}\n\n"
        f"--- \n"
        f"{history_text}\n\n"
        f"--- \n"
        f"🌤 **Погода у місті:** {weather}\n"
        f"💰 **Курс валют (НБУ):**\n{currency}"
    )

    # Надсилаємо в Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": full_message, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Повідомлення успішно надіслано!")
    except Exception as e:
        print(f"Помилка при надсиланні в Telegram: {e}")

if __name__ == "__main__":
    send_message()
