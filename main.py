import requests
from datetime import datetime

# Твої дані
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

def send_morning_post():
    now = datetime.now()
    date_key = now.strftime("%m-%d")
    date_str = now.strftime("%d.%m")

    # 1. Валюта
    try:
        cur = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json").json()
        usd = next(x for x in cur if x["cc"] == "USD")["rate"]
        eur = next(x for x in cur if x["cc"] == "EUR")["rate"]
        currency = f"💵 <b>Курс валют:</b> USD {usd:.2f} | EUR {eur:.2f}"
    except: currency = ""

    # 2. Дані з файлів
    names = get_from_github("names.txt", date_key)
    history = get_from_github("history.txt", date_key)
    
    # 3. Таймер
    days_to_ny = (datetime(now.year + 1, 1, 1) - now).days

    # Побудова професійної структури
    parts = []
    parts.append(f"☀️ <b>Доброго ранку! Сьогодні {date_str}</b>")
    
    if currency:
        parts.append(currency)
        
    if names:
        parts.append(f"😇 <b>День ангела святкують:</b>\n{names}")
        
    if history:
        parts.append(f"🕰 <b>Цей день в історії:</b>\n{history}")
    
    parts.append(f"🎄 До Нового року залишилось: <b>{days_to_ny}</b> днів")

    text = "\n\n".join(parts)

    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    send_morning_post()
