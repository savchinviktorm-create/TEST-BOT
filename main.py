import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
TELEGRAM_TOKEN = "8697253866:AAHx3nS_Bshn5bamwbdTQZCtOZ6pfT8tmjY"
TELEGRAM_CHAT_ID = "653398188"
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    # Обрізаємо під ліміт Telegram (1024 символи для фото)
    final_text = text[:1000] + "..." if len(text) > 1000 else text
    
    method = "sendPhoto" if photo_path and os.path.exists(photo_path) else "sendMessage"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "parse_mode": "HTML"
    }
    
    if method == "sendPhoto":
        payload["caption"] = final_text
        with open(photo_path, 'rb') as photo:
            return requests.post(url, data=payload, files={"photo": photo}).json()
    else:
        payload["text"] = final_text
        return requests.post(url, json=payload).json()

def get_currency():
    try:
        r = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd = next(i for i in r if i['ccy'] == 'USD')
        return f"🏦 <b>Приват:</b> USD: {usd['buy'][:5]} / {usd['sale'][:5]}"
    except: return "💰 Курс оновлюється..."

def get_cinema():
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:3]
        if not movies: return "🎬 Новинок поки немає."
        res = "🎟 <b>Кінопрем'єри:</b>\n"
        for m in movies:
            res += f"🍿 <b>{m['title']}</b>\n"
        return res
    except: return "🎬 Час у кіно!"

def make_post():
    divider = "─────────────────"
    text = (f"🧪 <b>ТЕСТОВИЙ ЗАПУСК</b>\n"
            f"{divider}\n"
            f"{get_cinema()}\n"
            f"{divider}\n"
            f"{get_currency()}")
    
    img = None
    for folder in ["media/evening", "media/morning"]:
        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if files:
                img = os.path.join(folder, random.choice(files))
                break
    return text, img

if __name__ == "__main__":
    content, photo = make_post()
    result = send_telegram(content, photo)
    print(f"Результат відправки: {result}")
