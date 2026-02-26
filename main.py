import os
import urllib.request
import urllib.parse
import json
from datetime import datetime

def get_weather(city, lat, lon, key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].capitalize()
            return f"🌡 **{city}**: {'+' if temp > 0 else ''}{temp}°C, {desc}"
    except Exception as e:
        return f"❌ {city}: помилка ({e})"

if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN")
    W_KEY = os.environ.get("WEATHER_API_KEY")
    CHAT_ID = os.environ.get("MY_CHAT_ID")
    
    text = f"📅 **Звіт на {datetime.now().strftime('%d.%m.%Y')}**\n\n"
    text += get_weather("с. Головецько", 49.1972, 23.4683, W_KEY) + "\n"
    text += get_weather("м. Львів", 49.8397, 24.0297, W_KEY)
    
    # Відправка через стандартну бібліотеку (без requests)
    data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}).encode()
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as f:
        print(f.read().decode())
