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
    # Telegram дозволяє до 4096 символів у текстовому повідомленні
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True # Щоб не вискакували посилання на сайти
    }
    return requests.post(url, json=payload).json()

def get_cinema_premieres():
    intros = [
        "🎟 <b>Свіжі кінопрем'єри тижня:</b>", 
        "🎬 <b>Що зараз дивляться в кінотеатрах:</b>", 
        "🍿 <b>Топ-5 новинок на великому екрані:</b>"
    ]
    try:
        # Запит на фільми, що зараз у прокаті в Україні
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:5] # Беремо рівно 5 фільмів
        
        if not movies: return "🎬 Нових прем'єр поки немає."
        
        res = f"{random.choice(intros)}\n\n"
        for m in movies:
            title = m.get('title', 'Без назви')
            desc = m.get('overview', 'Опис очікується...')
            # Робимо опис коротким (до 100 символів)
            short_desc = (desc[:97] + "...") if len(desc) > 100 else desc
            res += f"🍿 <b>{title}</b>\n└ {short_desc}\n\n"
        return res
    except:
        return "🎬 Похід у кіно — завжди гарна ідея!"

def make_post():
    divider = "─────────────────"
    now = get_now()
    
    cinema_block = get_cinema_premieres()
    
    text = (f"🗓 <b>ОГЛЯД НОВИНОК КІНО</b>\n"
            f"📍 Станом на: {now.strftime('%d.%m.%Y')}\n"
            f"{divider}\n\n"
            f"{cinema_block}"
            f"{divider}\n"
            f"✨ Приємного перегляду!")
    return text

if __name__ == "__main__":
    content = make_post()
    result = send_telegram(content)
    print(f"Результат відправки: {result}")
