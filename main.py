import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ (беруться з Secrets твого TEST-BOT) ---
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "583e99233cb332aaf8ab0ded7a92dde7")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/send{'Photo' if photo_path else 'Message'}"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "caption" if photo_path else "text": text, "parse_mode": "HTML"}
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
        res += f"🏦 <b>ПриватБанк:</b>\n└ USD: {usd_p['buy'][:5]} / {usd_p['sale'][:5]} | EUR: {eur_p['buy'][:5]} / {eur_p['sale'][:5]}\n"
    except: res += "⚠️ Курс тимчасово недоступний"
    return res

def get_random_lines(filename):
    path = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(path): return "Дані оновлюються..."
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.choice(lines) if lines else "Дані оновлюються..."
    except: return "Помилка файлу"

def get_random_image(folder):
    if not os.path.exists(folder): return None
    try:
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return os.path.join(folder, random.choice(files)) if files else None
    except: return None

def get_cinema_premieres():
    intros_cinema = [
        "🎟 <b>Новинки тижня в кіно:</b>", "🎬 <b>Прем'єрний четвер:</b>", 
        "🍿 <b>Вже в кінотеатрах України:</b>", "🎞 <b>Що подивитись на великому екрані:</b>"
    ]
    try:
        # Запит саме по регіону UA (Україна)
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:5] # Топ-5 фільмів
        
        if not movies: return "🎬 Сьогодні без гучних прем'єр."
        
        res = f"{random.choice(intros_cinema)}\n\n"
        for m in movies:
            title = m.get('title', 'Без назви')
            year = m.get('release_date', '----')[:4]
            desc = m.get('overview', 'Опис відсутній...')
            if len(desc) > 150: desc = desc[:147] + "..."
            
            res += f"🍿 <b>{title}</b> ({year})\n└ {desc}\n\n"
        return res
    except:
        return "🎬 Новинки кіно вже чекають на тебе!"

def make_test_post():
    now = get_now()
    divider = "✨ ✨ ✨ ✨ ✨"
    
    # Формуємо тестове повідомлення (без обмежень по часу)
    cinema = get_cinema_premieres()
    currency = get_currency_logic()
    fact = get_random_lines('facts')
    
    text = (f"🧪 <b>ТЕСТОВИЙ ЗАПУСК (КІНО-БЛОК)</b>\n"
            f"📅 Дата тесту: {now.strftime('%d.%m.%Y %H:%M')}\n"
            f"{divider}\n\n"
            f"{cinema}"
            f"{divider}\n"
            f"{currency}\n"
            f"{divider}\n"
            f"💡 <b>Цікавий факт:</b>\n└ {fact}")
    
    # Беремо будь-яку картинку з папок, якщо вони є
    img = get_random_image("media/evening") or get_random_image("media/morning")
    
    return text, img

if __name__ == "__main__":
    content, photo = make_test_post()
    result = send_telegram(content, photo)
    print(f"Результат відправки: {result}")
