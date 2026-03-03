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
    return requests.post(url, json=payload).json()

def get_trending_books():
    try:
        url = "https://www.googleapis.com/books/v1/volumes?q=language:uk&orderBy=newest&maxResults=10"
        data = requests.get(url, timeout=10).json()
        items = data.get('items', [])
        random.shuffle(items)
        res = "📖 <b>ТОП-3 КНИЖКОВИХ ТРЕНДІВ:</b>\n\n"
        for item in items[:3]:
            info = item.get('volumeInfo', {})
            title = info.get('title', 'Без назви')
            authors = ", ".join(info.get('authors', ['Автор невідомий']))
            desc = info.get('description', 'Опис відсутній...')
            limit = 300
            if len(desc) > limit:
                truncated = desc[:limit]
                last_point = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                desc = truncated[:last_point + 1] if last_point != -1 else truncated + "..."
            res += f"📚 <b>{title.upper()}</b>\n✍️ <i>{authors}</i>\n📝 {desc}\n\n"
        return res
    except: return "Книги тимчасово недоступні."

def get_cinema_premieres():
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:3] # Для тесту візьмемо 3, щоб не спамити
        res = "🎞 <b>ЗАРАЗ У КІНОТЕАТРАХ:</b>\n\n"
        for m in movies:
            res += f"🎬 <b>{m.get('title').upper()}</b>\n⭐ Рейтинг: {m.get('vote_average')}\n🍿 {m.get('overview')[:150]}...\n\n"
        return res
    except: return "Кіно афіша недоступна."

def test_preview():
    now = get_now()
    header = f"🗓 <b>ПРЕВ'Ю РУБРИК • {now.strftime('%d.%m.%Y')}</b>\n"
    line = "━━━━━━━━━━━━━━━━━━\n\n"
    
    # Генеруємо книжковий блок
    book_post = header + line + get_trending_books() + "🔖 <i>Смачної кави та цікавої книги!</i>"
    send_telegram(book_post)
    
    # Генеруємо кіно блок
    movie_post = header + line + get_cinema_premieres() + "✨ <i>Гарного перегляду!</i>"
    send_telegram(movie_post)

if __name__ == "__main__":
    test_preview()
    print("✅ Тестові пости відправ
