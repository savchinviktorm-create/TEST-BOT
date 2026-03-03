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
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/send{'Photo' if photo_path else 'Message'}"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "caption" if photo_path else "text": text, 
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            return requests.post(url, data=payload, files={"photo": photo}).json()
    return requests.post(url, json=payload).json()

# --- КНИЖКОВА ЛОГІКА (СЕРЕДА) ---
def get_trending_books():
    try:
        # Шукаємо найновіші та популярні книги українською
        url = "https://www.googleapis.com/books/v1/volumes?q=language:uk&orderBy=newest&maxResults=15"
        data = requests.get(url, timeout=10).json()
        items = data.get('items', [])
        random.shuffle(items)
        
        res = "📖 <b>ТРЕНДОВІ КНИГИ В УКРАЇНІ:</b>\n\n"
        count = 0
        for item in items:
            if count >= 3: break
            info = item.get('volumeInfo', {})
            title = info.get('title', 'Без назви')
            authors = ", ".join(info.get('authors', ['Автор невідомий']))
            category = ", ".join(info.get('categories', ['Література']))
            desc = info.get('description', 'Опис готується до друку...')

            # Розумне обрізання на крапці (до 350 символів)
            limit = 350
            if len(desc) > limit:
                truncated = desc[:limit]
                last_point = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                desc = truncated[:last_point + 1] if last_point != -1 else truncated + "..."
            
            res += f"📚 <b>{title.upper()}</b>\n"
            res += f"✍️ Автор: <i>{authors}</i>\n"
            res += f"🎭 Жанр: <i>{category}</i>\n"
            res += f"📝 {desc}\n\n"
            count += 1
        return res
    except:
        return "📖 Час відкрити нову цікаву книгу!"

# --- КІНО ЛОГІКА (ЧЕТВЕР) ---
def get_detailed_info(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=uk-UA&append_to_response=credits"
        data = requests.get(url, timeout=10).json()
        genres = ", ".join([g['name'] for g in data.get('genres', [])]) or "Кіно"
        cast = ", ".join([p['name'] for p in data.get('credits', {}).get('cast', [])[:3]]) or "Невідомо"
        return genres, cast
    except: return "Кіно", "Невідомо"

def get_cinema_premieres():
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:10]
        res = "🎞 <b>ЗАРАЗ У КІНОТЕАТРАХ УКРАЇНИ:</b>\n\n"
        for m in movies:
            g, c = get_detailed_info(m.get('id'))
