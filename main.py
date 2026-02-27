import requests
from datetime import datetime

TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
CHAT_ID = "653398188"

def get_from_github(file_name, date_key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.startswith(date_key):
                    return line[6:].strip()
    except: return None
    return None

def send_daily_report():
    now = datetime.now()
    date_key = now.strftime("%m-%d")
    date_display = now.strftime("%d.%m.%Y")

    # 1. Валюта
    try:
        cur = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json").json()
        usd = next(x for x in cur if x["cc"] == "USD")["rate"]
        eur = next(x for x in cur if x["cc"] == "EUR")["rate"]
        currency = f"🇺🇸 USD: {usd:.2f} | 🇪🇺 EUR: {eur:.2f}"
    except: currency = "Курс недоступний"

    # 2. Дані з файлів
    names = get_from_github("names.txt", date_key)
    history = get_from_github("history.txt", date_key)
    joke = get_from_github("jokes.txt", date_key) # Якщо є такий файл

    # 3. Таймер
    days_to_ny = (datetime(now.year + 1, 1, 1) - now).days

    # Збірка повідомлення
    text = f"📅 <b>ЗВІТ НА {date_display}</b>\n"
    text += f"──────────────────\n"
    text += f"💰 <b>Курс валют (НБУ):</b>\n{currency}\n\n"
    
    if names:
        text += f"😇 <b>Іменини дня:</b>\n{names}\n"
        text += "✨ <i>Не забудь привітати іменинників!</i>\n\n"
        
    if history:
        text += f"🕰 <b>Цей день в історії:</b>\n{history}\n\n"
        
    if joke:
        text += f"😆 <b>Хвилинка гумору:</b>\n{joke}\n\n"
    
    text += f"🎄 <b>До Нового року:</b> {days_to_ny} днів"

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    send_daily_report()
