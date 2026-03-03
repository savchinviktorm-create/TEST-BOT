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

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    return requests.post(url, json=payload).json()

def get_detailed_info(movie_id):
    """Отримує жанри та акторів для конкретного фільму"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=uk-UA&append_to_response=credits"
        data = requests.get(url, timeout=10).json()
        
        # Отримуємо жанри
        genres = [g['name'] for g in data.get('genres', [])]
        genres_str = ", ".join(genres) if genres else "Не вказано"
        
        # Отримуємо топ-3 акторів
        cast = [person['name'] for person in data.get('credits', {}).get('cast', [])[:3]]
        cast_str = ", ".join(cast) if cast else "Інформація відсутня"
        
        return genres_str, cast_str
    except:
        return "Кіно", "Невідомо"

def get_cinema_premieres():
    intros = ["🎟 <b>Зараз у кінопрокаті:</b>", "🎬 <b>Новинки тижня (включаючи мультфільми):</b>"]
    try:
        # Отримуємо список фільмів у прокаті
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:5]
        
        if not movies: return "🎬 Нових прем'єр поки немає."
        
        res = f"{random.choice(intros)}\n\n"
        for m in movies:
            title = m.get('title', 'Без назви')
            movie_id = m.get('id')
            
            # Отримуємо деталі (жанр та акторів)
            genres, cast = get_detailed_info(movie_id)
            
            res += f"🍿 <b>{title.upper()}</b>\n"
            res += f"🎭 Жанр: <i>{genres}</i>\n"
            res += f"👥 У ролях: <i>{cast}</i>\n\n"
        return res
    except:
        return "🎬 Похід у кіно — завжди гарна ідея!"

def make_post():
    divider = "─────────────────"
    now = get_now()
    cinema_block = get_cinema_premieres()
    
    text = (f"🗓 <b>КІНОАФІША УКРАЇНИ</b>\n"
            f"📍 {now.strftime('%d.%m.%Y')}\n"
            f"{divider}\n\n"
            f"{cinema_block}"
            f"{divider}\n"
            f"✨ Приємного перегляду!")
    return text

if __name__ == "__main__":
    content = make_post()
    result = send_telegram(content)
    print(f"Результат: {result}")
