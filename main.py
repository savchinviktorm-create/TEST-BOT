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
    """Шукає дані за форматом MM-DD (перші 5 символів рядка)"""
    try:
        today_str = get_now().strftime("%m-%d") # Результат "03-01"
        if not os.path.exists(filename): return "Файл не знайдено"
        
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip()[:5] == today_str:
                    # Повертаємо все, що після перших 5 символів (дати)
                    content = line.strip()[5:].strip()
                    # Прибираємо можливі початкові тире, крапки чи пробіли
                    content = content.lstrip(' —-–:.') 
                    return content
        return "Дані відсутні"
    except: return "Помилка"

def get_random_lines(filename, count=1):
    try:
        if not os.path.exists(filename): return ["Дані відсутні"]
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.sample(lines, min(len(lines), count)) if lines else ["Дані відсутні"]
    except: return ["Помилка"]

def days_to_ny():
    today = get_now().date()
    ny = datetime.date(today.year + 1, 1, 1)
    return (ny - today).days

def make_post():
    now = get_now()
    divider = "✨ ✨ ✨ ✨ ✨"

    congratulation_calls = [
        "Не забудьте привітати знайомих, якщо вони серед вашого кола друзів! 🥂",
        "Чудова нагода зателефонувати друзям та привітати їх! 🎈",
        "Якщо маєте знайомих з цими іменами — обов'язково надішліть їм вітання! 🎁",
        "Маленьке повідомлення імениннику зробить його день кращим! 💌",
        "Поділіться радістю з друзями, які сьогодні святкують! ✨",
        "Привітання — це дрібниця, яка дуже зігріває серце. Напишіть їм! 😊",
        "Сьогодні гарний день, щоб згадати про знайомих іменинників! ☀️",
        "Встигніть побажати всього найкращого винуватцям свята! 🎂",
        "Ангели люблять, коли їхніх підопічних вітають! 👼",
        "Ваше привітання сьогодні буде дуже доречним! 🧸",
        "Не тримайте добро в собі — привітайте друзів! 🕊",
        "Зробіть приємний сюрприз сьогоднішнім іменинникам! 🎀",
        "Ваш дзвінок може стати найкращим подарунок! 📱",
        "Сьогодні імена звучать як пісня. Приєднайтеся до вітань! 🎶",
        "Згадайте, хто з ваших близьких сьогодні святкує! 👀",
        "Маєте друзів з цими іменами? Напишіть їм пару теплих слів! 🔥",
        "Даруйте усмішки та привітання сьогодні! 💐",
        "Щирі слова завжди доречні. Вітаємо разом! 🌟",
        "Нехай ваші друзі відчують вашу увагу сьогодні! 💎",
        "Сьогодні день сповнений світла для цих імен. Поділіться ним! 🕯",
        "Гарна нагода відновити спілкування через привітання! 🤝",
        "Не забудьте надіслати листівку або тепле слово! 📮",
        "Свято стає кращим, коли про нього пам'ятають друзі! 🎊",
        "Сьогоднішні іменинники чекають на вашу увагу! 🍭",
        "Складіть коротке вітання для близьких! ✍️",
        "Хай ваш привітальний пост або смс зігріє когось! 🧣",
        "Ви знаєте, що робити — теплі слова самі себе не напишуть! 😉",
        "Сьогодні іменинники заслуговують на ваші обійми (хоча б віртуальні)! 🤗",
        "Будьте першим, хто привітає сьогоднішніх героїв дня! 🥇",
        "Світ стає добрішим від щирих привітань! 🌎"
    ]

    advice_intros = ["💡 Порада:", "🛠 Лайфхак:", "🧠 Хитрість:", "✨ Пропозиція:", "📝 На замітку:"]

    # Збір даних
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
    img_folder = "media/morning"
    photo = None
    if os.path.exists(img_folder):
        files = [f for f in os.listdir(img_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if files:
            photo = os.path.join(img_folder, random.choice(files))
    
    send_telegram(content, photo)
