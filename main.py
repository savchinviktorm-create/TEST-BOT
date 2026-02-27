import os
import urllib.request
import json
import csv
import io
from datetime import datetime

# Твоє пряме посилання
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSExxHF9GN-lpJF9I3L9kLzFoH9lo4_emwtiEoHpiezlf3ESOw6dxGrjmQwk1wuFC6mV6035wu6-l4M/pub?gid=2060076239&single=true&output=csv"

def get_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8')
    except: return None

def parse_table():
    raw = get_data(URL_CSV)
    if not raw: return None
    
    # Робимо плоский список усіх значень з таблиці
    f = io.StringIO(raw)
    reader = csv.reader(f)
    data = []
    for row in reader:
        data.extend([cell.strip() for cell in row if cell.strip()])

    def get_val(keyword, offset=1):
        """Шукає слово і склеює число з наступною клітинкою (копійками)"""
        for i, word in enumerate(data):
            if keyword.lower() in word.lower():
                try:
                    # Склеюємо ціле + копійки (напр. 56 і 1500)
                    val = f"{data[i+offset]}.{data[i+offset+1][:2]}"
                    return float(val)
                except: continue
        return 0.0

    # Витягуємо валюту
    u_buy = get_val("USD", 1)
    u_sale = get_val("USD", 3)
    e_buy = get_val("EUR", 1)
    e_sale = get_val("EUR", 3)
    
    # Витягуємо пальне (тепер реально з таблиці!)
    a95 = get_val("А-95", 1)
    dp = get_val("ДП", 1)
    gas = get_val("Газ", 1)

    cross = round(e_buy / u_buy, 3) if u_buy > 0 else 0

    return {
        "cur": f"🇺🇸 **USD:** {u_buy} / {u_sale}\n🇪🇺 **EUR:** {e_buy} / {e_sale}\n💱 **Крос-курс:** {cross}",
        "fuel": f"⛽ **Пальне:**\nА-95: {a95} грн\nДП: {dp} грн\nГаз: {gas} грн"
    }

def get_weather():
    key = os.getenv('WEATHER_API_KEY')
    locs = [("Головецько", "lat=49.20&lon=23.45"), ("Львів", "q=Lviv")]
    out = []
    for name, p in locs:
        d = get_data(f"http://api.openweathermap.org/data/2.5/weather?{p}&appid={key}&units=metric&lang=uk")
        if d:
            js = json.loads(d)
            out.append(f"📍 {name}: {round(js['main']['temp'])}°C, {js['weather'][0]['description'].capitalize()}")
    return "\n".join(out)

def get_git_info(file_name, key):
    d = get_data(f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}")
    if d:
        for line in d.splitlines():
            if key.lower() in line.lower():
                return line.split('—', 1)[-1].strip() if '—' in line else line.strip()
    return "дані відсутні"

def send():
    now = datetime.now()
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    day_month = f"{now.day} {months[now.month-1]}"

    info = parse_table()
    currency_text = info['cur'] if info else "⚠️ Помилка валют"
    fuel_text = info['fuel'] if info else "⚠️ Помилка пального"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют:**\n{currency_text}\n\n"
        f"⛽ **Ціни на пальне:**\n{fuel_text}\n\n"
        f"😇 **Іменини:**\n{day_month}: {get_git_info('names.txt', day_month)}\n\n"
        f"📜 **Історія:**\n{get_git_info('history.txt', now.strftime('%m-%d'))}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    url = f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage"
    payload = json.dumps({"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send()
