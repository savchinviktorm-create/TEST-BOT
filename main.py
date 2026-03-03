import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
# Для тесту можна вписати ключі прямо тут або залишити os.environ
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
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                return requests.post(url, data=payload, files={"photo": photo}).json()
        return requests.post(url, json=payload).json()
    except Exception as e:
        return {"error": str(e)}

# --- КНИЖКОВА ЛОГІКА (СЕРЕДА) ---
def get_trending_books():
    try:
        url = "https://www.googleapis.com/books/v1/volumes?q=language:uk&orderBy=newest&maxResults=15"
        r = requests.get(url, timeout=10)
        data = r.json()
        items = data.get('items', [])
        if not items:
            return "📖 Сьогодні без новинок, але старі добрі книги завжди поруч!"
            
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
        if not movies:
            return "🎬 Нових прем'єр поки немає."
            
        res = "🎞 <b>ЗАРАЗ У КІНОТЕАТРАХ УКРАЇНИ:</b>\n\n"
        for m in movies:
            g, c = get_detailed_info(m.get('id'))
            res += f"🎬 <b>{m.get('title', 'Фільм').upper()}</b>\n🎭 <i>{g}</i>\n👥 <i>{c}</i>\n\n"
        return res
    except: return "🎬 Час обрати фільм!"

# --- ОСНОВНИЙ КОНСТРУКТОР ---
def make_post():
    now = get_now()
    wd = now.weekday() # 0-Пн, 1-Вт, 2-Ср, 3-Чт
    
    book_wishes = [
        "📚 Смачної кави та цікавої книги!", 
        "📖 Час зануритися у нову історію!", 
        "🔖 Нехай ця книга надихне вас!", 
        "📗 Приємного читання!"
    ]
    movie_wishes = [
        "🎬 Гарного перегляду!", 
        "🍿 Не забудьте попкорн!", 
        "🌟 Магії великого екрана вам!", 
        "🎞 Життя — це кіно!"
    ]

    # Якщо сьогодні СЕРЕДА (wd == 2) - відправляємо книги
    if wd == 2:
        text = (f"🗓 <b>КНИЖКОВА СЕРЕДА • {now.strftime('%d.%m.%Y')}</b>\n"
                f"📚📖📚📖📚📖📚📖📚\n\n"
                f"{get_trending_books()}"
                f"🔖 {random.choice(book_wishes)}")
        return text, None

    # Якщо сьогодні ЧЕТВЕР (wd == 3) - відправляємо кіно
    elif wd == 3:
        text = (f"🗓 <b>КІНОАФІША • {now.strftime('%d.%m.%Y')}</b>\n"
                f"🎬✨🎬✨🎬✨🎬✨🎬\n\n"
                f"{get_cinema_premieres()}"
                f"⭐️🍿⭐️🍿⭐️🍿⭐️🍿⭐️\n"
                f"✨ {random.choice(movie_wishes)}")
        return text, None

    # Для тесту в будь-який інший день (наприклад, сьогодні)
    else:
        # Щоб протестувати книги зараз, просто розкоментуй рядок нижче:
        # return f"🧪 ТЕСТ КНИГ:\n\n{get_trending_books()}", None
        return f"🤖 Сьогодні {now.strftime('%A')}. Спецпости виходять у середу та четвер о 16:00.", None

if __name__ == "__main__":
    content, photo = make_post()
    result = send_telegram(content, photo)
    print(result)
