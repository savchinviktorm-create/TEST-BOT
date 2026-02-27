import os
import requests
from datetime import datetime

def get_nbu():
    try:
        # НБУ додав поле special, але в JSON воно просто ігнорується кодом
        r = requests.get("https://bank.gov.ua/NBUStatService/v1/statistictic/exchange?json", timeout=10).json()
        usd = next(i['rate'] for i in r if i['cc'] == 'USD')
        eur = next(i['rate'] for i in r if i['cc'] == 'EUR')
        return f"🇺🇸 {usd:.2f} | 🇪🇺 {eur:.2f}"
    except:
        return "немає даних"

def get_privat():
    try:
        r = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5", timeout=10).json()
        usd = next(i for i in r if i['ccy'] == 'USD')
        eur = next(i for i in r if i['ccy'] == 'EUR')
        return f"🇺🇸 {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | 🇪🇺 {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except:
        return "немає даних"

def send():
    nbu = get_nbu()
    pb = get_privat()
    now = datetime.now()
    
    # Тільки те, що працює 100%
    text = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"🏛 **КУРС НБУ:**\n{nbu}\n\n"
        f"🏦 **ПРИВАТБАНК:**\n{pb}\n\n"
        f"⛽ **ПАЛЬНЕ (СЕРЕДНІ ЦІНИ):**\n"
        f"🔹 А-95: ~56.40 грн\n"
        f"🔹 ДП: ~52.80 грн\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    url = f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage"
    requests.post(url, json={"chat_id": os.getenv('MY_CHAT_ID'), "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
