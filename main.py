import requests
import os
from datetime import datetime

# Секрети
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_test():
    now = datetime.now()
    date_key = now.strftime("%m-%d")
    
    # 1. Курс валют
    try:
        cur = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json").json()
        usd = next(x for x in cur if x["cc"] == "USD")["rate"]
        currency_text = f"🇺🇸 USD: {usd:.2f}"
    except:
        currency_text = "Курс недоступний"

    # 2. Таймер до НР
    days_left = (datetime(now.year + 1, 1, 1) - now).days

    # Формуємо просте повідомлення (без іменин поки, щоб не ламалося)
    text = (
        f"🚀 <b>Бот Працює!</b>\n"
        f"📅 Дата: {now.strftime('%d.%m.%Y')}\n"
        f"💰 {currency_text}\n"
        f"🎄 До Нового року: {days_left} днів"
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
    
    if r.status_code == 200:
        print("✅ ПЕРЕМОГА! Повідомлення в Телеграмі.")
    else:
        print(f"❌ ПОМИЛКА: {r.status_code}")
        print(f"Відповідь від Telegram: {r.text}")

if __name__ == "__main__":
    send_test()
