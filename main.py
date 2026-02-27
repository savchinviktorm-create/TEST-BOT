import requests
import random
import io
from datetime import datetime
import pytz

# --- КОНФІГУРАЦІЯ ---
TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
CHAT_ID = "653398188"
GITHUB_BASE = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/"
TMDB_API_KEY = "3fd2be6f0c70a2a598f084ddadd75477" # Твій ключ для кіно

def get_from_github(file_name):
    """Отримує дані з файлів на GitHub"""
    try:
        r = requests.get(f"{GITHUB_BASE}{file_name}", timeout=10)
        if r.status_code == 200:
            return [l.strip() for l in r.text.splitlines() if l.strip()]
    except: return []
    return []

# --- API СЕРВІСИ ---

def get_holidays():
    try:
        year = datetime.now().year
        r = requests.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/UA", timeout=5).json()
        today = datetime.now().strftime("%Y-%m-%d")
        holidays = [h['localName'] for h in r if h['date'] == today]
        return "🎊 <b>Свята сьогодні:</b> " + ", ".join(holidays) if holidays else ""
    except: return ""

def get_fact():
    try:
        day, month = datetime.now().day, datetime.now().month
        r = requests.get(f"http://numbersapi.com/{month}/{day}/date", timeout=5)
        return f"💡 <b>Цікавий факт:</b>\n<i>{r.text}</i>"
    except: return ""

def get_advice():
    try:
        r = requests.get("https://api.adviceslip.com/advice", timeout=5).json()
        # Порада приходить англійською. Можна залишити так або додати переклад пізніше.
        return f"🛠 <b>Порада дня:</b>\n<i>{r['slip']['advice']}</i>"
    except: return "🛠 <b>Порада дня:</b> Посміхайтеся частіше, це вам личить!"

def get_movie():
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}&language=uk-UA"
        r = requests.get(url, timeout=5).json()
        movie = random.choice(r['results'])
        return f"🎬 <b>Вечірній кінозал:</b>\n\n<b>{movie['title']}</b>\n⭐️ Рейтинг: {movie['vote_average']:.1f}/10\n\n📖 {movie['overview'][:250]}..."
    except: return "🎬 <b>Вечірній кінозал:</b> Сьогодні час для перегляду вашого улюбленого фільму!"

def get_currency():
    res = "💰 <b>Курси валют:</b>\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd = next(x for x in p if x['ccy'] == 'USD')
        eur = next(x for x in p if x['ccy'] == 'EUR')
        res += f"🏦 <b>Приват:</b> 🇺🇸 {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | 🇪🇺 {float(eur['buy']):.2f}/{float(eur['sale']):.2f}\n"
    except: res += "🏦 ПриватБанк: сервіс оновлюється\n"
    
    try:
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=5).json()
        u_m = next(x for x in m if x['currencyCodeA'] == 840 and x['currencyCodeB'] == 980)
        e_m = next(x for x in m if x['currencyCodeA'] == 978 and x['currencyCodeB'] == 980)
        res += f"🖤 <b>Моно:</b> 🇺🇸 {u_m['rateBuy']:.2f}/{u_m['rateSell']:.2f} | 🇪🇺 {e_m['rateBuy']:.2f}/{e_m['rateSell']:.2f}\n"
    except: pass
    return res

# --- ОСНОВНІ БЛОКИ ЗА ЧАСОМ ---

def send_morning():
    """РАНОК: Фото + Валюти + Свята + Іменини + Історія"""
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
    try:
        img_data = requests.get(img_url).content
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                      files={"photo": ("i.png", img_data)}, data={"chat_id": CHAT_ID, "caption": text, "parse_mode": "HTML"})
    except:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def send_midday():
    """ОБІД: Мотивація + Факт дня"""
    quotes = get_from_github("quotes.txt")
    quote = random.choice(quotes) if quotes else "Кожен день — це новий шанс!"
    fact = get_fact()
    
    text = f"✨ <b>ХВИЛИНКА НАТХНЕННЯ</b>\n\n«{quote}»\n\n{fact}"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def send_evening():
    """ВЕЧІР: Порада + Анекдот + Кіно"""
    advice = get_advice()
    movie = get_movie()
    
    # Отримуємо випадковий анекдот
    jokes = get_from_github("jokes.txt")
    joke = random.choice(jokes) if jokes else "Сьогодні без жартів, просто гарного вечора!"
    
    text = f"{advice}\n\n"
    text += f"😂 <b>Хвилинка гумору:</b>\n{joke}\n\n"
    text += f"──────────────────\n{movie}"
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    hour = datetime.now(kyiv_tz).hour
    
    if 5 <= hour <= 10:
        send_morning()
    elif 11 <= hour <= 16:
        send_midday()
    elif 18 <= hour <= 23:
        send_evening()
    else:
        # Для ручного тесту в неробочий час присилаємо вечірній блок
        send_evening()
