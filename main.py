import requests
import random
import io
from datetime import datetime
import pytz

# --- КОНФІГУРАЦІЯ ---
TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
CHAT_ID = "653398188"
GITHUB_BASE = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/"
# Перевір цей ключ або отримай новий на themoviedb.org
TMDB_API_KEY = "3fd2be6f0c70a2a598f084ddadd75477" 

def get_from_github(file_name):
    try:
        r = requests.get(f"{GITHUB_BASE}{file_name}", timeout=10)
        if r.status_code == 200:
            lines = [l.strip() for l in r.text.splitlines() if l.strip()]
            return lines
    except: return []
    return []

# --- ФУНКЦІЇ КОНТЕНТУ ---

def get_holidays():
    try:
        year = datetime.now().year
        r = requests.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/UA", timeout=5).json()
        today = datetime.now().strftime("%Y-%m-%d")
        holidays = [h['localName'] for h in r if h['date'] == today]
        return "🎊 <b>Свята сьогодні:</b> " + ", ".join(holidays) if holidays else ""
    except: return ""

def get_currency():
    res = "💰 <b>Курси валют:</b>\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd = next(x for x in p if x['ccy'] == 'USD')
        eur = next(x for x in p if x['ccy'] == 'EUR')
        res += f"🏦 <b>Приват:</b> 🇺🇸 {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | 🇪🇺 {float(eur['buy']):.2f}/{float(eur['sale']):.2f}\n"
    except: res += "🏦 ПриватБанк: оновлення...\n"
    
    try:
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=5).json()
        u_m = next(x for x in m if x['currencyCodeA'] == 840 and x['currencyCodeB'] == 980)
        e_m = next(x for x in m if x['currencyCodeA'] == 978 and x['currencyCodeB'] == 980)
        res += f"🖤 <b>Моно:</b> 🇺🇸 {u_m['rateBuy']:.2f}/{u_m['rateSell']:.2f} | 🇪🇺 {e_m['rateBuy']:.2f}/{e_m['rateSell']:.2f}\n"
    except: pass
    return res

def get_movie_ukr():
    """Спроба взяти фільм з API українською, або повернення цікавого факту про кіно"""
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}&language=uk-UA"
        r = requests.get(url, timeout=5).json()
        if 'results' in r and r['results']:
            movie = random.choice(r['results'])
            title = movie.get('title', 'Цікавий фільм')
            desc = movie.get('overview', 'Опис скоро з’явиться...')
            rating = movie.get('vote_average', 0)
            return f"🎬 <b>Вечірній кінозал:</b>\n\n<b>{title}</b>\n⭐️ Рейтинг: {rating:.1f}/10\n\n📖 {desc[:300]}..."
    except: pass
    return "🎬 <b>Вечірній кінозал:</b>\nСьогодні чудовий час, щоб переглянути українську класику або світові новинки в українському дубляжі! Попкорн обов'язковий. 🍿"

# --- ОСНОВНІ БЛОКИ ---

def send_morning():
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    now = datetime.now(kyiv_tz)
    date_key = now.strftime("%m-%d")
    
    names = next((l[6:] for l in get_from_github("names.txt") if l.startswith(date_key)), "дані відсутні")
    history = next((l[6:] for l in get_from_github("history.txt") if l.startswith(date_key)), "подій не знайдено")
    holidays = get_holidays()
    
    text = f"☀️ <b>Доброго ранку! Сьогодні {now.strftime('%d.%m.%Y')}</b>\n"
    if holidays: text += f"{holidays}\n"
    text += "──────────────────\n"
    text += get_currency() + "\n"
    text += f"😇 <b>Іменини:</b> {names}\n\n"
    text += f"🕰 <b>Цей день в історії:</b>\n{history}\n\n"
    text += f"🎄 До Нового року: <b>{(datetime(now.year+1,1,1,tzinfo=kyiv_tz)-now).days}</b> днів"

    img_url = f"{GITHUB_BASE}media/morning/{random.randint(1, 26)}.png"
    img_data = requests.get(img_url).content
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                  files={"photo": ("i.png", img_data)}, data={"chat_id": CHAT_ID, "caption": text, "parse_mode": "HTML"})

def send_midday():
    quotes = get_from_github("quotes.txt")
    quote = random.choice(quotes) if quotes else "Сьогодні чудовий день!"
    # Тимчасово прибрав англійський факт, замінив на суто українську цитату з емодзі
    text = f"✨ <b>ХВИЛИНКА НАТХНЕННЯ</b>\n\n«{quote}»\n\n🌈 <i>Бажаємо продуктивного дня!</i>"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def send_evening():
    # Порада з файлу (українською)
    advices = get_from_github("advices.txt")
    advice = random.choice(advices) if advices else "Будьте собою, всі інші ролі зайняті."
    
    # Анекдот
    jokes = get_from_github("jokes.txt")
    joke = random.choice(jokes) if jokes else "Сьогодні вечір релаксу, без жартів!"
    
    # Фільм
    movie = get_movie_ukr()
    
    text = f"🛠 <b>Порада дня:</b>\n<i>{advice}</i>\n\n"
    text += f"😂 <b>Хвилинка гумору:</b>\n{joke}\n\n"
    text += f"──────────────────\n{movie}"
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    hour = datetime.now(pytz.timezone('Europe/Kyiv')).hour
    if 5 <= hour <= 10:
        send_morning()
    elif 11 <= hour <= 16:
        send_midday()
    else:
        send_evening()
