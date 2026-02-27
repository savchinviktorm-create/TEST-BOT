import requests
from datetime import datetime

# Твої дані (вставлені напряму для надійності)
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
    except:
        return None
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
    except:
        currency = "Курс тимчасово недоступний"

    # 2. Дані з файлів
    names = get_from_github("names.txt", date_key)
    history = get_from_github("history.txt", date_key)
    
    # 3. Таймер до НР
    days_to_ny = (datetime(now.year + 1, 1, 1) - now).days

    # Формування тексту
    text = f"📅 <b>ЗВІТ НА {date_display}</b>\n\n"
    
    text += f"💰 <b>Курс валют (НБУ):</b>\n{currency}\n\n"
    
    if names:
        text += f"😇 <b>В цей день свої іменини святкують:</b>\n{names}\n"
        text += "✨ <i>Не забудь привітати, якщо серед твого кола оточення є люди з такими іменами.</i>\n\n"
        
    if history:
        text += f"🕰 <b>Цей день в історії:</b>\n{history}\n\n"
    
    text += f"🎄 <b>До Нового року залишилось:</b> {days_to_ny} днів"

    # Відправка
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("✅ ПЕРЕМОГА! Повідомлення надіслано.")
    else:
        print(f"❌ ПОМИЛКА {r.status_code}: {r.text}")

if __name__ == "__main__":
    send_daily_report()
