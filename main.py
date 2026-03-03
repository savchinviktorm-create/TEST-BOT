import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
TELEGRAM_TOKEN = "8056086259:AAFf5q-Mh9eEa_Kx4G9pW6B_LAnY5C7R_rE"
TELEGRAM_CHAT_ID = "653398188"
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    # Обрізаємо під ліміт Telegram (1024 символи для фото)
    final_text = text[:1020] + "..." if len(text) > 1024 else text
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/send{'Photo' if photo_path else 'Message'}"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "caption" if photo_path else "text": final_text, 
        "parse_mode": "HTML"
    }
    
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            return requests.post(url, data=payload, files={"photo": photo}).json()
    return requests.post(url, json=payload).json()

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        res += f"🏦 <b>Приват:</b> USD: {usd_p['buy'][:5]}/{usd_p['sale'][:5]} | EUR: {eur_p['buy'][:5]}/{eur_p['sale'][:5]}\n"
    except: res += "⚠️ Курс недоступний\n"
    return res

def get_random_lines(filename):
    path = f"{filename}.txt"
    if not os.path.exists(path): return "Факт вже готується..."
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.choice(lines) if lines else "Дані оновлюються..."
    except: return "Дані оновлюються..."

def get_random_image(folder):
    if not os.path.exists(folder): return None
    try:
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return os.path.join(folder, random.choice(files)) if files else None
    except: return None

def get_cinema_premieres():
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:5]
        
        if not movies: return "🎬 Нових прем'єр поки немає."
        
        res = "🎟 <b>Кінопрем'єри тижня:</b>\n\n"
        for m in movies:
            title = m.get('title', 'Фільм')
            desc = m.get('overview', 'Без опису...')
            desc_short = desc[:80] + "..." if len(desc) > 80 else desc
            res += f"🍿 <b>{title}</b>\n└ {desc_short}\n\n"
        return res
    except: return "🎬 Час у кіно!"

def make_test_post():
    now = get_now()
    divider = "─────────────────"
    
    cinema = get_cinema_premieres()
    currency = get_currency_logic()
    fact = get_random_lines('facts')
    
    text = (f"🧪 <b>ТЕСТ КІНО-БЛОКУ</b>\n"
            f"📅 {now.strftime('%d.%m.%Y %H:%M')}\n"
            f"{divider}\n"
            f"{cinema}"
            f"{divider}\n"
            f"{currency}"
            f"{divider}\n"
            f"💡 <b>Факт:</b> {fact}")
    
    img = get_random_image("media/evening") or get_random_image("media/morning")
    return text, img

if __name__ == "__main__":
    content, photo = make_test_post()
    result = send_telegram(content, photo)
    print(f"Результат відправки: {result}")
