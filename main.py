import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

def get_weather(city_name, lat, lon, api_key):
    """Отримує погоду для вказаних координат."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=uk"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].capitalize()
            # Додаємо знак + для плюсової температури
            sign = "+" if temp > 0 else ""
            return f"📍 {city_name}: {sign}{temp}°C, {desc}"
    except Exception as e:
        return f"📍 {city_name}: не вдалося отримати дані ❌"

def send_telegram(token, chat_id, text):
    """Надсилає повідомлення в Telegram."""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML' # Дозволяє робити текст жирним через <b>
        }
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as f:
            return True
    except Exception as e:
        print(f"Помилка Telegram: {e}")
        return False

if __name__ == "__main__":
    # Завантаження секретів
    TOKEN = os.environ.get("TOKEN", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()

    # Дата для заголовка
    date_now = datetime.now().strftime('%d.%m.%Y')
    
    # Формування звіту
    header = f"<b>ЗВІТ НА {date_now}</b>\n\n"
    
    # Отримання погоди (твої координати)
    weather_gol = get_weather("Головецько", 49.19, 23.46, W_KEY)
    weather_lviv = get_weather("Львів", 49.83, 24.02, W_KEY)
    
    full_report = header + weather_gol + "\n" + weather_lviv + "\n\n"
    full_report += "Бот працює стабільно! ✅"

    # Відправка
    if TOKEN and CHAT_ID:
        if send_telegram(TOKEN, CHAT_ID, full_report):
            print("Звіт успішно відправлено!")
        else:
            print("Помилка при відправці.")
    else:
        print("Секрети TOKEN або CHAT_ID порожні!")
