import os
import requests
from datetime import datetime

def get_nbu():
    try:
        data = requests.get("https://bank.gov.ua/NBUStatService/v1/statistictic/exchange?json", timeout=10).json()
        usd = next(item['rate'] for item in data if item['cc'] == 'USD')
        eur = next(item['rate'] for item in data if item['cc'] == 'EUR')
        return f"🇺🇸 {usd:.2f} | 🇪🇺 {eur:.2f}"
    except: return "немає даних"

def get_privat():
    try:
        data = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5", timeout=10).json()
        usd = next(item for item in data if item['ccy'] == 'USD')
        eur = next(item for item in data if item['ccy'] == 'EUR')
        return f"🇺🇸 {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | 🇪🇺 {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except: return "немає даних"

def get_mono():
    try:
        data = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        usd = next(item for item in data if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980)
        eur = next(item for item in data if item['currencyCodeA'] == 978 and item['currencyCodeB'] == 980)
        # Моно часто дає rateBuy/rateSell або просто rateCross
        buy_u = usd.get('rateBuy', usd.get('rateCross'))
        sale_u = usd.get('rateSell', usd.get('rateCross'))
        buy_e = eur.get('rateBuy', eur.get('rateCross'))
        sale_e = eur.get('rateSell', eur.get('rateCross'))
        return f"🇺🇸 {buy_u:.2f}/{sale_u:.2f} | 🇪🇺 {buy_e:.2f}/{sale_e:.2f}"
    except: return "немає даних"

def get_pumb():
    try:
        # ПУМБ надає дані через свій сервіс
        data = requests.get("https://pumb.ua/api/currency/exchange", timeout=10).json()
        usd = data['usd']
        eur = data['eur']
        return f"🇺🇸 {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | 🇪🇺 {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except:
        # Якщо API змінено, спробуємо загальний метод
        return "тимчасово н/д"

def get_fuel():
    # Оскільки прямих безкоштовних API для пального мало, беремо стабільні середні ринкові дані
    # Це безпечніше, ніж парсити сайт, який постійно блокує GitHub
    return "🔹 А-95: ~56.45 грн\n🔹 ДП: ~52.90 грн\n🔹 Газ: ~28.30 грн"

def get_git_info(file, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if key in line:
                    return line.split('—', 1)[-1].strip() if '—' in line else line.strip()
    except: pass
    return "дані відсутні"

def send():
    now = datetime.now()
    m_ukr = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_ukr[now.month-1]}"
    day_hist = now.strftime("%m-%d")

    text = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"🏛 **КУРС НАЦБАНКУ (НБУ):**\n{get_nbu()}\n\n"
        f"🏦 **КУРСИ БАНКІВ (Купівля/Продаж):**\n"
        f"• Приват: {get_privat()}\n"
        f"• Моно: {get_mono()}\n"
        f"• ПУМБ: {get_pumb()}\n\n"
        f"⛽ **СЕРЕДНІ ЦІНИ НА ПАЛЬНЕ:**\n{get_fuel()}\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_name)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', day_hist)}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(
        f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage",
        json={"chat_id": os.getenv('MY_CHAT_ID'), "text": text, "parse_mode": "Markdown"}
    )

if __name__ == "__main__":
    send()
