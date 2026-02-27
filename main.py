import requests
import random
import io
from datetime import datetime
import pytz

# --- НАЛАШТУВАННЯ ---
TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
CHAT_ID = "653398188"
GITHUB_RAW = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/"

# --- ДОПОМІЖНІ ФУНКЦІЇ ---

def get_text_from_github(file_name, date_key=None):
    """Отримує текст: або за датою (02-27), або весь список (для цитат)"""
    try:
        r = requests.get(f"{GITHUB_RAW}{file_name}", timeout=10)
        if r.status_code != 200: return None
        
        lines = [l.strip() for l in r.text.splitlines() if l.strip()]
        
        if date_key:  # Шукаємо конкретну дату (для ранку)
            for line in lines:
                if line.startswith(date_key):
                    return line[6:].strip()
            return None
        return lines  # Повертаємо весь список (для цитат)
    except:
        return None

def get_currency():
    """Отримує свіжий курс валют"""
    try:
        res = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json", timeout=10).json()
        usd = next(x for x in res if x["cc"] == "USD")["rate"]
        eur = next(x for x in res if x["cc"] == "EUR")["rate"]
        return f"💵 <b>Курс валют:</b> USD {usd:.2f} | EUR {eur:.2f}"
    except:
        return ""

# --- ОСНОВНІ БЛОКИ КОНТЕНТУ ---

def send_morning_post():
    """08:00 - Ранок: Картинка + Валюта + Іменини + Історія"""
    now = datetime.now(pytz.timezone('Europe/Kyiv'))
    date_key = now.strftime("%m-%d")
    
    names = get_text_from_github("names.txt", date_key)
    history = get_text_from_github("history.txt", date_key)
    days_to_ny = (datetime(now.year + 1, 1, 1).date() - now.date()).days

    # Текст повідомлення
    parts = [f"☀️ <b>Доброго ранку! Сьогодні {now.strftime('%d.%m')}</b>"]
    currency = get_currency()
    if currency: parts.append(currency)
    if names: parts.append(f"😇 <b>День ангела:</b> {names}")
    if history: parts.append(f"🕰 <b>Цей день в історії:</b>\n{history}")
    parts.append(f"🎄 До Нового року: <b>{days_to_ny}</b> днів")
    
    caption = "\n\n".join(parts)

    # Випадкова картинка (1-26)
    img_num = random.randint(1, 26)
    img_url = f"{GITHUB_RAW}media/morning/{img_num}.png"
    
    try:
        img_res = requests.get(img_url)
        if img_res.status_code == 200:
            photo = io.BytesIO(img_res.content)
            photo.name = "morning.png"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                          files={"photo": photo}, data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"})
        else:
            raise Exception("No image")
    except:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": caption, "parse_mode": "HTML"})

def send_quote_post():
    """11:00 - Мотивація: Випадкова цитата з емодзі"""
    quotes = get_text_from_github("quotes.txt")
    if not quotes: return

    quote = random.choice(quotes)
    emojis = ["✨", "🌟", "💡", "🚀", "💎", "🌈", "🔥", "🎯", "🌱", "☀️", "🙌", "🔋", "⚡️", "🏆"]
    e1, e2 = random.sample(emojis, 2)

    text = f"{e1} <b>ХВИЛИНКА МОТИВАЦІЇ</b> {e1}\n\n«{quote}»\n\n{e2} <i>Бажаємо продуктивного дня!</i>"
    
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

# --- ГОЛОВНИЙ ПЕРЕМИКАЧ ---

if __name__ == "__main__":
    # Визначаємо час у Києві
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    now_hour = datetime.now(kyiv_tz).hour

    # Логіка розподілу постів по годинах
    if 6 <= now_hour <= 8:
        print("Запуск: Ранковий звіт")
        send_morning_post()
    elif 9 <= now_hour <= 11:
        print("Запуск: Цитата дня")
        send_quote_post()
    else:
        # Для ручного запуску через кнопку, якщо час не в діапазоні
        print("Запуск вручну: Надсилаю цитату за замовчуванням")
        send_quote_post()
