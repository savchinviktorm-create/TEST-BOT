import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "583e99233cb332aaf8ab0ded7a92dde7")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "653398188")
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

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=10).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        eur_m = next(i for i in m if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        
        res += f"🏦 <b>ПриватБанк:</b>\n└ USD: {usd_p['buy'][:5]} / {usd_p['sale'][:5]} | EUR: {eur_p['buy'][:5]} / {eur_p['sale'][:5]}\n"
        res += f"🐾 <b>Монобанк:</b>\n└ USD: {usd_m['rateBuy']:.2f} / {usd_m['rateSell']:.2f} | EUR: {eur_m['rateBuy']:.2f} / {eur_m['rateSell']:.2f}"
    except:
        res += "⚠️ Курс тимчасово недоступний"
    return res

def get_data_by_date(filename):
    """Шукає дані за форматом MM-DD з твоїх файлів"""
    try:
        today_str = get_now().strftime("%m-%d")
        if not os.path.exists(filename): 
            return "Файл не знайдено"
        
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                clean_line = line.strip()
                if clean_line.startswith(today_str):
                    # Відрізаємо дату (5 символів) та будь-які пробіли/тире після неї
                    content = clean_line[5:].lstrip(' -:').strip()
                    return content if content else "Сьогодні без подій"
        return "Дані відсутні для цієї дати"
    except Exception as e:
        return f"Помилка зчитування"

def get_random_lines(filename, count=1):
    try:
        if not os.path.exists(filename): return ["Дані відсутні"]
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.sample(lines, min(len(lines), count)) if lines else ["Дані відсутні"]
    except: return ["Помилка файлу"]

def days_to_ny():
    today = get_now().date()
    ny = datetime.date(today.year + 1, 1, 1)
    return (ny - today).days

def make_post():
    now = get_now()
    # Красивий розділювач, який не "ламається" на різних екранах
    divider = "✨ ✨ ✨ ✨ ✨"

    congratulation_calls = [
        "Не забудьте привітати знайомих! 🥂", "Маленьке SMS зробить їхній день кращим! 💌",
        "Зробіть приємний сюрприз іменинникам! 🎀", "Чудова нагода зателефонувати близьким! 🎈",
        "Поділіться радістю з друзями! ✨", "Ваш дзвінок — найкращий подарунок! 📱"
    ]

    advice_intros = ["💡 Порада:", "🛠 Лайфхак:", "🧠 Хитрість:", "✨ Пропозиція:", "📝 На замітку:"]

    # Отримуємо дані з твоїх файлів (Holiday.txt та Wiking.txt)
    names = get_data_by_date('history.txt')
    holidays = get_data_by_date('Holiday.txt')
    history = get_data_by_date('Wiking.txt')
    advice = get_random_lines('advices.txt', 1)[0]
    
    text = (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n"
            f"📅 Сьогодні: <b>{now.strftime('%d.%m.%Y')}</b>\n"
            f"{divider}\n"
            f"🎂 <b>Іменини сьогодні святкують:</b>\n"
            f"└ 👤 {names}\n"
            f"<i>{random.choice(congratulation_calls)}</i>\n\n"
            f"🎉 <b>Свята:</b> {holidays}\n"
            f"📜 <b>Цей день в історії:</b> {history}\n"
            f"{divider}\n"
            f"{get_currency_logic()}\n"
            f"🎄 До Нового Року: {days_to_ny()} дн.\n"
            f"{divider}\n"
            f"{random.choice(advice_intros)}\n"
            f"└ {advice}")
            
    return text

if __name__ == "__main__":
    content = make_post()
    # Логіка вибору фото
    img_folder = "media/morning"
    photo = None
    if os.path.exists(img_folder):
        files = [f for f in os.listdir(img_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if files:
            photo = os.path.join(img_folder, random.choice(files))
    
    send_telegram(content, photo)
