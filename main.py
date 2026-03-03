import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
TELEGRAM_TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
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

# --- СПЕЦІАЛЬНІ РУБРИКИ ---

def get_trending_books():
    try:
        url = "https://www.googleapis.com/books/v1/volumes?q=intitle:книга+l:uk&orderBy=relevance&maxResults=15"
        items = requests.get(url, timeout=15).json().get('items', [])
        if not items: return "📖 Книжкова полиця оновлюється..."
        random.shuffle(items)
        res = "📖 <b>ТОП-3 КНИЖКОВИХ ТРЕНДІВ:</b>\n\n"
        count = 0
        for item in items:
            if count >= 3: break
            info = item.get('volumeInfo', {})
            desc = info.get('description', '')
            if not desc or len(desc) < 30: continue
            title, authors = info.get('title', 'Без назви'), ", ".join(info.get('authors', ['Невідомо']))
            limit = 350
            if len(desc) > limit:
                truncated = desc[:limit]
                last_dot = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                desc = truncated[:last_dot + 1] if last_dot != -1 else truncated + "..."
            res += f"📚 <b>{title.upper()}</b>\n✍️ <i>{authors}</i>\n📝 {desc}\n\n"
            count += 1
        return res
    except: return "📖 Час почитати щось цікаве!"

def get_cinema_premieres():
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        movies = requests.get(url, timeout=10).json().get('results', [])[:10]
        res = "🎞 <b>ЗАРАЗ У КІНОТЕАТРАХ УКРАЇНИ:</b>\n\n"
        for m in movies:
            res += f"🎬 <b>{m.get('title').upper()}</b>\n⭐ Рейтинг: {m.get('vote_average')}\n🍿 {m.get('overview')[:180]}...\n\n"
        return res
    except: return "🎬 Час обрати фільм для вечора!"

# --- СТАНДАРТНІ ДАНІ ---

def get_currency():
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd = next(i for i in p if i['ccy'] == 'USD')
        eur = next(i for i in p if i['ccy'] == 'EUR')
        return f"💰 <b>КУРС:</b> USD {usd['buy'][:5]}/{usd['sale'][:5]} | EUR {eur['buy'][:5]}/{eur['sale'][:5]}"
    except: return "💰 Курс тимчасово недоступний"

def get_file_data(filename, by_date=False):
    path = f"{filename}.txt"
    if not os.path.exists(path): return "Дані оновлюються"
    with open(path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if by_date:
        today = get_now().strftime("%m-%d")
        for l in lines:
            if l.startswith(today): return l[5:].lstrip(' —-–:.')
        return "Сьогодні без подій"
    return random.choice(lines) if lines else "Дані оновлюються"

def get_random_image(folder):
    if not os.path.exists(folder): return None
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(folder, random.choice(files)) if files else None

# --- КОНСТРУКТОР ПОСТА ---

def make_post():
    now = get_now()
    h, wd = now.hour, now.weekday()
    date_str = now.strftime('%d.%m.%Y')

    # 1. КНИЖКОВА СЕРЕДА (Середа 16:00)
    if wd == 2 and h == 16:
        return f"🗓 <b>КНИЖКОВА СЕРЕДА • {date_str}</b>\n----------------------------------\n\n{get_trending_books()}🔖 <i>Приємного читання!</i>", None

    # 2. КІНОАФІША (Четвер 16:00)
    if wd == 3 and h == 16:
        return f"🗓 <b>КІНОАФІША • {date_str}</b>\n----------------------------------\n\n{get_cinema_premieres()}✨ <i>Гарного перегляду!</i>", None

    # 3. РАНКОВИЙ ПОСТ (05:00 - 10:59)
    if 5 <= h < 11:
        img = get_random_image("media/morning")
        text = (f"🌅 <b>ДОБРОГО РАНКУ! {date_str}</b>\n\n"
                f"🎂 <b>Іменини:</b> {get_file_data('history', True)}\n"
                f"🎉 <b>Свята:</b> {get_file_data('Holiday', True)}\n"
                f"📜 <b>Цей день в історії:</b> {get_file_data('Wiking', True)}\n\n"
                f"{get_currency()}\n\n"
                f"💡 <b>Порада:</b> {get_file_data('advices')}")
        return text, img

    # 4. ВЕЧІРНІЙ ПОСТ (20:00+)
    if h >= 20 or h < 5:
        img = get_random_image("media/evening")
        text = (f"💡 {get_file_data('advices')}\n\n"
                f"🧐 {get_file_data('facts')}\n\n"
                f"🎬 <b>Вечірній кінозал:</b> {get_file_data('movies', False)}") # Або API версія
        return text, img

    # 5. ДЕННИЙ ПОСТ (решта часу)
    img = get_random_image("media/evening")
    return f"💡 {get_file_data('advices')}\n\n🧐 {get_file_data('facts')}", img

if __name__ == "__main__":
    content, photo = make_post()
    send_telegram(content, photo)
