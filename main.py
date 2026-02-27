import requests
import os
from datetime import datetime

# Налаштування
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Kyiv"

def get_data(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text
    except:
        return None

def get_names(search_key):
    """Шукає іменини за ключем MM-DD (наприклад 02-27)"""
    url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/names.txt"
    data = get_data(url)
    if data:
        for line in data.splitlines():
            if line.startswith(search_key):
                return line[6:].strip()
    return None

def get_history(search_key):
    """Шукає історію за ключем MM-DD"""
    url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/history.txt"
    data = get_data(url)
    if data:
        for line in data.splitlines():
            if line.startswith(search_key):
                return line[6:].strip()
    return None

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url).json()
        return f"{round(res['main']['temp'])}°C, {res['weather'][0]['description'].capitalize()}"
    except:
        return None

def send_message():
    now = datetime.now()
    date_key = now.strftime("%m-%d") # Формат 02-27
    date_display = now.strftime("%d.%m.%Y")

    names = get_names(date_key)
    history = get_history(date_key)
    weather = get_weather()

    # Збірка повідомлення
    parts = [f"📅 <b>ЗВІТ НА {date_display}</b>"]

    if names:
        parts.append(f"😇 <b>В цей день свої іменини святкують:</b>\n{names}\n\n✨ <i>Не забудь привітати близьких, якщо серед твого оточення є люди з такими іменами. Їм буде приємно!</i>")

    if history:
        parts.append(f"🕰 <b>Цей день в історії:</b>\n{history}")

    # Блок погоди
    if weather:
        parts.append(f"──────────────────\n🌤 <b>Погода:</b> {weather}")

    full_text = "\n\n".join(parts)

    # Відправка (HTML режим найнадійніший)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": full_text, "parse_mode": "HTML"}
    
    r = requests.post(url, data=payload)
    print(f"Статус відправки: {r.status_code}")

if __name__ == "__main__":
    send_message()
