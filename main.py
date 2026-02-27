import requests
import random
import datetime
import os

# --- ТВОЇ КЛЮЧІ ТА ДАНІ (ВЖЕ ВСТАВЛЕНО) ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
HOLIDAY_API_KEY = "17904126938947f694726e6423985558"
TELEGRAM_TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
TELEGRAM_CHAT_ID = "653398188"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"Статус відправки: {r.status_code}")
        if r.status_code != 200:
            print(f"Помилка від Telegram: {r.text}")
        return r.json()
    except Exception as e:
        print(f"Помилка зв'язку: {e}")
        return None

def get_divider():
    # Різноманітні розділювачі для кожного дня
    divs = [
        "\n<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n",
        "\n✨ <b>• • • • • • • • • • •</b> ✨\n",
        "\n<b>──────────────────────</b>\n",
        "\n🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹 🔹\n",
        "\n<b>◈━━━━━━━━━━━━━━━━━━━━◈</b>\n"
    ]
    return random.choice(divs)

def get_full_currency():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    try:
        # ПриватБанк
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=10).json()
        u = next(i for i in p if i['ccy'] == 'USD')
        e = next(i for i in p if i['ccy'] == 'EUR')
        res += f"🏦 Приват: 🇺🇸 {u['buy'][:5]}/{u['sale'][:5]} | 🇪🇺 {e['buy'][:5]}/{e['sale'][:5]}\n"
    except:
        res += "🏦 Приват: Оновлюється...\n"
    
    try:
        # Монобанк
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        res += f"🐱 Моно (USD): {usd_m['rateBuy']}/{usd_m['rateSell']}\n"
    except:
        pass
    return res

def get_holidays():
    now = datetime.datetime.now()
    url = f"https://holidays.abstractapi.com/v1/?api_key={HOLIDAY_API_KEY}&country=UA&year={now.year}&month={now.month}&day={now.day}"
    try:
        r = requests.get(url, timeout=10).json()
        if r and isinstance(r, list):
            h_names = [h['name'] for h in r]
            return "🎊 <b>СВЯТА:</b> " + ", ".join(h_names)
        return "🎊 <b>СВЯТА:</b> Офіційних свят сьогодні немає"
    except:
        return "🎊 <b>СВЯТА:</b> Інформація оновлюється"

def get_movie():
    try:
        page = random.randint(1, 15)
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={page}"
        r = requests.get(url, timeout=10).json()
        m = random.choice(r['results'])
        return f"🎬 <b>ВЕЧІРНІЙ КІНОЗАЛ</b>\n🎥 <b>{m.get('title', 'Фільм')}</b>\n⭐ Рейтинг: {m.get('vote_average', '7.0')}\n🍿 {m.get('overview', 'Опис скоро буде...')[:250]}..."
    except:
        return "🎬 Подивіться сьогодні щось із топ-рейтингу!"

def get_line(file):
    try:
        if not os.path.exists(file): return "Дані оновлюються"
        with open(file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return random.choice(lines) if lines else "Дані відсутні"
    except:
        return "Інформація недоступна"

def make_post():
    # Час за Києвом (UTC+2)
    hour = (datetime.datetime.utcnow().hour + 2) % 24 
    
    div1 = get_divider()
    div2 = get_divider()
    
    if 5 <= hour < 11:
        today = datetime.date.today()
        ny = datetime.date(today.year + (1 if today.month == 12 and today.day > 31 else 0), 1, 1)
        return (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n📅 Сьогодні: {today.strftime('%d.%m.%Y')}\n{div1}"
                f"🎂 Іменини: {get_line('names.txt')}\n{get_holidays()}\n📜 Історія: {get_line('history.txt')}\n"
                f"{div2}{get_full_currency()}\n🎄 До НР: {(ny-today).days} дн.\n"
                f"{div1}💡 Лайфхак: {get_line('advices.txt')}")
    
    elif 11 <= hour < 18:
        return f"🌤 <b>ДЕННИЙ ВИПУСК</b>\n\n💡 Лайфхак: {get_line('advices.txt')}\n{div1}🧐 Факт: {get_line('facts.txt')}"
    
    else:
        return (f"🌙 <b>ВЕЧІРНІЙ ПОСТ</b>\n\n💡 Лайфхак: {get_line('advices.txt')}\n{div1}"
                f"🧐 Факт: {get_line('facts.txt')}\n{div1}😂 Жарт: {get_line('jokes.txt')}\n"
                f"{div2}{get_movie()}")

if __name__ == "__main__":
    content = make_post()
    send_telegram(content)
