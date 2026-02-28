import requests
import random
import datetime
import os
import pytz

# Налаштування (використовуємо твої ключі)
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
TELEGRAM_TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
TELEGRAM_CHAT_ID = "653398188"

# Часовий пояс Києва
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    if photo_path and os.path.exists(photo_path):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": text, "parse_mode": "HTML"}
            files = {"photo": photo}
            r = requests.post(url, data=payload, files=files)
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        r = requests.post(url, json=payload)
    return r.json()

def get_random_image(folder):
    if not os.path.exists(folder): return None
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(folder, random.choice(files)) if files else None

def get_data_by_date(filename):
    """Шукає рядок за форматом ММ-ДД (напр. 02-28)"""
    try:
        today_str = get_now().strftime("%m-%d")
        if not os.path.exists(filename): return "Дані оновлюються"
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(today_str):
                    return line[6:].strip() # Пропускаємо 'ММ-ДД '
        return "На сьогодні подій не знайдено"
    except:
        return "Помилка читання файлу"

def get_random_lines(filename, count=1):
    try:
        if not os.path.exists(filename): return ["Дані відсутні"]
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines: return ["Дані відсутні"]
        return random.sample(lines, min(len(lines), count))
    except:
        return ["Інформація недоступна"]

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ (Середній)</b>\n"
    try:
        # Приват
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=10).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        
        # Моно
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        
        # Розрахунок середнього (крос-курс)
        avg_buy = (float(usd_p['buy']) + float(usd_m['rateBuy'])) / 2
        avg_sale = (float(usd_p['sale']) + float(usd_m['rateSell'])) / 2
        
        res += f"🇺🇸 USD: {usd_p['buy'][:5]}/{usd_p['sale'][:5]} (Сер: {avg_buy:.2f})\n"
        res += f"🇪🇺 EUR: {eur_p['buy'][:5]}/{eur_p['sale'][:5]}\n"
        res += f"🐱 Моно USD: {usd_m['rateBuy']}/{usd_m['rateSell']}"
    except:
        res += "⚠️ Курс тимчасово недоступний"
    return res

def days_to_ny():
    today = get_now().date()
    ny = datetime.date(today.year + 1, 1, 1)
    return (ny - today).days

def get_movie():
    try:
        page = random.randint(1, 10)
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={page}"
        r = requests.get(url, timeout=10).json()
        m = random.choice(r['results'])
        return f"🎬 <b>ВЕЧІРНІЙ КІНОЗАЛ</b>\n🎥 <b>{m.get('title')}</b>\n⭐ Рейтинг: {m.get('vote_average')}\n🍿 {m.get('overview')[:200]}..."
    except: return "🎬 Подивіться сьогодні щось цікаве!"

def make_post():
    now = get_now()
    hour = now.hour
    minute = now.minute
    
    # --- 1) РАНКОВИЙ ПОСТ (5:00 - 10:00) ---
    if 5 <= hour < 11:
        img = get_random_image("media/morning")
        text = (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n📅 Сьогодні: {now.strftime('%d.%m.%Y')}\n"
                f"━━━━━━━━━━━━━━\n"
                f"🎂 Іменини: {get_data_by_date('history.txt')}\n"
                f"🎉 Свята: {get_data_by_date('Holiday.txt')}\n"
                f"📜 Цей день в історії: {get_data_by_date('Wiking.txt')}\n"
                f"━━━━━━━━━━━━━━\n"
                f"{get_currency_logic()}\n"
                f"🎄 До Нового Року: {days_to_ny()} дн.\n"
                f"━━━━━━━━━━━━━━\n"
                f"💡 Лайфхак: {get_random_lines('advices.txt')[0]}")
        return text, img

    # --- 2) ПОСТ ОБ 11:00 ---
    elif 11 <= hour < 13:
        img = get_random_image("media/evening")
        q = get_random_lines('quotes.txt')[0]
        a = get_random_lines('advices.txt')[0]
        m = get_random_lines('database.txt')[0]
        text = f"✨ <b>НАТХНЕННЯ ТА ПОРАДИ</b>\n\n💬 {q}\n\n🛠 {a}\n\n🚀 {m}"
        return text, img

    # --- 3) ПОСТ О 13:30 ---
    elif 13 <= hour < 17:
        img = get_random_image("media/evening")
        advs = get_random_lines('advices.txt', 2)
        facts = get_random_lines('facts.txt', 3)
        text = "🍕 <b>ДЕННИЙ ДАЙДЖЕСТ</b>\n\n🛠 <b>Лайфхаки:</b>\n— " + "\n— ".join(advs) + "\n\n🧐 <b>Факти:</b>\n— " + "\n— ".join(facts)
        return text, img

    # --- 4) ПОСТ О 17:00 ---
    elif 17 <= hour < 20:
        img = get_random_image("media/evening")
        facts = get_random_lines('facts.txt', 2)
        advs = get_random_lines('advices.txt', 3)
        text = "☕ <b>ВЕЧІРНІЙ МІКС</b>\n\n🧐 <b>Факти:</b>\n— " + "\n— ".join(facts) + "\n\n🛠 <b>Лайфхаки:</b>\n— " + "\n— ".join(advs)
        return text, img

    # --- 5) ВЕЧІРНІЙ ПОСТ (Після 20:00) ---
    else:
        img = get_random_image("media/evening")
        a = get_random_lines('advices.txt')[0]
        f = get_random_lines('facts.txt')[0]
        j = get_random_lines('jokes.txt')[0]
        text = f"🌙 <b>ЗАВЕРШЕННЯ ДНЯ</b>\n\n🛠 {a}\n\n🧐 {f}\n\n😂 {j}\n\n{get_movie()}"
        return text, img

if __name__ == "__main__":
    content, photo = make_post()
    send_telegram(content, photo)
