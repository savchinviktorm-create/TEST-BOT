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
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=uk-UA&append_to_response=credits"
        data = requests.get(url, timeout=10).json()
        genres = [g['name'] for g in data.get('genres', [])]
        genres_str = ", ".join(genres) if genres else "Кіно"
        cast = [person['name'] for person in data.get('credits', {}).get('cast', [])[:3]]
        cast_str = ", ".join(cast) if cast else "Інформація відсутня"
        return genres_str, cast_str
    except:
        return "Кіно", "Інформація відсутня"

def get_cinema_premieres():
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=uk-UA&region=UA"
        r = requests.get(url, timeout=10).json()
        movies = r.get('results', [])[:10]
        
        if not movies: return "🎬 Нових прем'єр поки немає."
        
        res = "🎞 <b>ЗАРАЗ У КІНОТЕАТРАХ:</b>\n\n"
        for m in movies:
            title = m.get('title', 'Без назви')
            movie_id = m.get('id')
            genres, cast = get_detailed_info(movie_id)
            res += f"🎬 <b>{title.upper()}</b>\n"
            res += f"🎭 <i>{genres}</i>\n"
            res += f"👥 <i>{cast}</i>\n\n"
        return res
    except:
        return "🎬 Час обрати фільм для вечора!"

def make_post():
    # Красиві розділювачі замість ліній
    cinema_divider = "🎬✨🎬✨🎬✨🎬✨🎬"
    bottom_divider = "⭐️🍿⭐️🍿⭐️🍿⭐️🍿⭐️"
    
    now = get_now()
    
    final_wishes = [
        "✨ Приємного перегляду!", "🍿 Не забудьте про попкорн!", "🎬 До зустрічі у кінозалі!", 
        "📽 Гарного вечора за переглядом!", "🌟 Нехай фільм перевершить очікування!", 
        "🎫 Квитки вже чекають на вас!", "🎭 Емоційного перегляду!", "🥤 Велика кола сама себе не вип'є!", 
        "🧐 Обирайте серцем, дивіться очима!", "🌈 Магії великого екрана вам!", 
        "🎞 Життя — це кіно, обирайте найкраще!", "🤫 Тиші у залі та яскравих вражень!", 
        "🛋 Влаштовуйтеся зручніше!", "👀 Побачимось на прем'єрі!", "🕯 Атмосферного вам вечора!", 
        "🤘 Нехай фільм буде драйвовим!", "🧠 Їжі для роздумів після сеансу!", 
        "💙 Підтримуйте українські кінотеатри!", "💛 До зустрічі на головному екрані міста!", 
        "🤩 Нехай цей фільм стане вашим улюбленим!", "🥳 Веселого перегляду всією компанією!", 
        "💘 Ідеальний план для побачення!", "🔥 Буде гаряче, не пропустіть!", 
        "🌑 Час зануритися у темряву кінозалу!", "⚡️ Заряджайтеся енергією кіно!", 
        "🤖 Навіть роботи люблять хороші фільми!", "🦄 Казкових емоцій від перегляду!", 
        "🧩 Зберіть свій пазл вражень!", "🛶 Вперед назустріч пригодам!", 
        "💎 Знайдіть свій кінодіамант!", "📣 Поділіться потім враженнями!", 
        "🕰 Час для кіно завжди вчасно!", "👒 Дивіться красиво!", "👟 Взувайтеся і біжіть у кіно!", 
        "🌌 Нескінченних вам кіновсесвітів!", "🥇 Тільки найкращих прем'єр!", 
        "🎁 Кіно — це завжди подарунок для душі!", "🪁 Легкого перегляду!", 
        "🧸 Навіть дітям буде цікаво!", "🛸 Космічного задоволення від картинки!", 
        "🛡 Будьте героями власного життя!", "🗝 Відкрийте для себе нову історію!", 
        "🪁 Нехай фантазія не має меж!", "⚖️ Оберіть свій ідеальний жанр!", 
        "🧱 Будуйте плани на вихідні навколо кіно!", "🌋 Вибухових емоцій!", 
        "❄️ Зігрівайтеся атмосферою кінозалу!", "🍃 Свіжих вражень від новинок!", 
        "🐾 Слідуйте за цікавим сюжетом!", "🦾 Міцного здоров'я та гарного кіно!"
    ]
    
    cinema_block = get_cinema_premieres()
    wish = random.choice(final_wishes)
    
    # Формуємо текст так, щоб у сповіщенні (перші рядки) було видно суть
    text = (f"🗓 <b>КІНОАФІША • {now.strftime('%d.%m.%Y')}</b>\n"
            f"{cinema_divider}\n\n"
            f"{cinema_block}"
            f"{bottom_divider}\n"
            f"✨ {wish}")
    return text

if __name__ == "__main__":
    content = make_post()
    result = send_telegram(content)
    print(f"Результат відправки: {result}")
