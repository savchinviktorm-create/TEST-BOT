import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.text, 'html.parser')
    except: return None

def clean_val(text):
    """Витягує тільки перше числове значення (курс)"""
    res = re.sub(r'[^\d,.]', '', text).replace(',', '.')
    return res[:5] if len(res) > 5 else res

def parse_data():
    # 1. ВАЛЮТИ
    res = {"usd": "н/д", "eur": "н/д", "u_val": 0.0, "e_val": 0.0}
    soup_curr = get_soup("https://finance.i.ua/")
    if soup_curr:
        rows = soup_curr.find_all('tr')
        for row in rows:
            txt = row.get_text().upper()
            cols = row.find_all('td')
            if len(cols) >= 3:
                buy = clean_val(cols[1].get_text(strip=True))
                sale = clean_val(cols[2].get_text(strip=True))
                if "USD" in txt and res["usd"] == "н/д":
                    res["usd"] = f"{buy} / {sale}"
                    try: res["u_val"] = float(buy)
                    except: pass
                elif "EUR" in txt and res["eur"] == "н/д":
                    res["eur"] = f"{buy} / {sale}"
                    try: res["e_val"] = float(buy)
                    except: pass

    # 2. ПАЛЬНЕ
    fuel = {"a95": "н/д", "dp": "н/д", "gas": "н/д"}
    soup_fuel = get_soup("https://finance.i.ua/fuel/")
    if soup_fuel:
        for row in soup_fuel.find_all('tr'):
            t = row.get_text()
            cols = row.find_all('td')
            # Шукаємо рядок з середніми цінами
            if "Середня" in t and len(cols) >= 4:
                fuel["a95"] = cols[2].get_text(strip=True)
                fuel["dp"] = cols[3].get_text(strip=True)
            # Газ зазвичай в окремому блоці або таблиці
            if "Газ" in t and len(cols) >= 2 and fuel["gas"] == "н/д":
                fuel["gas"] = cols[1].get_text(strip=True)
    return res, fuel

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
    curr, fuel = parse_data()
    now = datetime.now()
    
    cross = round(curr['e_val'] / curr['u_val'], 3) if curr['u_val'] > 0 else "н/д"
    
    # Виправлення для іменин (шукаємо "27 лютого")
    m_ukr = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_ukr[now.month-1]}"
    day_hist = now.strftime("%m-%d")

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс (finance.i.ua):**\n🇺🇸 USD: {curr['usd']}\n🇪🇺 EUR: {curr['eur']}\n💱 Крос-курс: {cross}\n\n"
        f"⛽ **Пальне (i.ua):**\n🔹 А-95: {fuel['a95']} грн\n🔹 ДП: {fuel['dp']} грн\n🔹 Газ: {fuel['gas']} грн\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_name)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', day_hist)}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
