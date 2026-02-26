import os
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime

def get_weather(city, lat, lon, key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].capitalize()
            return f"📍 {city}: {'+' if temp > 0 else ''}{temp}°C, {desc}"
    except: return f"📍 {city}: дані недоступні"

def get_currency():
    try:
        url = "https://api.monobank.ua/bank/currency"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            usd = next(item for item in data if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980)
            eur = next(item for item in data if item['currencyCodeA'] == 978 and item['currencyCodeB'] == 980)
            return f"💵 USD: {usd['rateBuy']}/{usd['rateSell']}\n💶 EUR: {eur['rateBuy']}/{eur['rateSell']}"
    except: return "📈 Курс валют: тимчасово недоступний"

def days_to_new_year():
    now = datetime.now()
    next_year = now.year + 1
    ny_date = datetime(next_year, 1, 1)
    diff = ny_date - now
    return f"🎄 До Нового року залишилося: <b>{diff.days}</b> днів!"

def get_history_by_date(file_name):
    """Шукає рядок, що починається з поточної дати (напр. 26.02)."""
    today_prefix = datetime.now().strftime('%d.%m') # Отримуємо "26.02"
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(today_prefix):
                    return line.strip()
    return f"📜 {today_prefix}: Сьогодні спокійний день в історії..."

def get_random_line(file_name, default_text):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            return random.choice(lines) if lines else default_text
    return default_text

def send_telegram(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        data = urllib.parse.urlencode(params).encode()
        urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=15)
        return True
    except: return False

if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()

    date_full = datetime.now().strftime('%d.%m.%Y')
    
    report = [
        f"<b>📅 ЗВІТ НА {date_full}</b>\n",
        get_weather("Головецько", 49.19, 23.46, W_KEY),
        get_weather("Львів", 49.83, 24.02, W_KEY) + "\n",
        
        "<b>💰 Курс валют (Mono):</b>",
        get_currency() + "\n",
        
        "<b>😇 Іменини сьогодні:</b>",
        get_random_line("names.txt", "Дані відсутні") + "\n",
        
        "<b>📜 Цей день в історії:</b>",
        get_history_by_date("history.txt") + "\n",
        
        "<b>💡 Цитата дня:</b>",
        f"<i>\"{get_random_line('database.txt', 'Живи сьогодні!')}\"</i>\n",
        
        "<b>😂 Анекдот дня:</b>",
        get_random_line("jokes.txt", "Сьогодні без жартів...") + "\n",
        
        days_to_new_year() + "\n",
        "<i>Бот працює стабільно! ✅</i>"
    ]

    full_text = "\n".join(report)
    send_telegram(TOKEN, CHAT_ID, full_text)
