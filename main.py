import os
import requests
from datetime import datetime

def get_data():
    # 1. КУРС ВАЛЮТ (Офіційний API НБУ - найнадійніше джерело)
    # Це гарантує точність без зайвих цифр
    res = {"usd": "н/д", "eur": "н/д", "u_val": 1.0, "e_val": 1.0}
    try:
        data = requests.get("https://bank.gov.ua/NBUStatService/v1/statistictic/exchange?json", timeout=10).json()
        for curr in data:
            if curr['cc'] == 'USD':
                res["usd"] = f"{curr['rate']:.2f}"
                res["u_val"] = curr['rate']
            elif curr['cc'] == 'EUR':
                res["eur"] = f"{curr['rate']:.2f}"
                res["e_val"] = curr['rate']
    except: pass

    # 2. ПАЛЬНЕ (Стабільний API або перевірений шлях)
    fuel = {"a95": "56.40", "dp": "52.90", "gas": "28.50"} # Базові середні значення як резерв
    try:
        # Спроба отримати свіжі дані (спрощений парсинг без складних таблиць)
        f_req = requests.get("https://api.minfin.com.ua/fuel/average/", timeout=10).json()
        fuel["a95"] = f_req.get("a95", {}).get("bid", fuel["a95"])
        fuel["dp"] = f_req.get("diezel", {}).get("bid", fuel["dp"])
        fuel["gas"] = f_req.get("gas", {}).get("bid", fuel["gas"])
    except: pass
    
    return res, fuel

def get_git_info(file, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if key in line:
                    return line.split('—', 1)[-1].strip()
    except: pass
    return "немає даних"

def send():
    curr, fuel = get_data()
    now = datetime.now()
    
    # Крос-курс НБУ
    cross = round(curr['e_val'] / curr['u_val'], 2)
    
    m_ukr = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_ukr[now.month-1]}"
    day_hist = now.strftime("%m-%d")

    # Складаємо повідомлення максимально просто, щоб уникнути SyntaxError
    text = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Офіційний курс НБУ:**\n"
        f"🇺🇸 USD: {curr['usd']} грн\n"
        f"🇪🇺 EUR: {curr['eur']} грн\n"
        f"💱 Крос-курс: {cross}\n\n"
        f"⛽ **Середні ціни на пальне:**\n"
        f"🔹 А-95: {fuel['a95']} грн\n"
        f"🔹 ДП: {fuel['dp']} грн\n"
        f"🔹 Газ: {fuel['gas']} грн\n\n"
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
