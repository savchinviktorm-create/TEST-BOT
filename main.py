import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.text, 'html.parser')
    except: return None

def parse_currency():
    """Курс валют з finance.i.ua"""
    soup = get_soup("https://finance.i.ua/")
    res = {"usd": "н/д", "eur": "н/д", "u_val": 0.0, "e_val": 0.0}
    if not soup: return res
    
    table = soup.find('table', class_='table-delta')
    if table:
        for row in table.find_all('tr'):
            txt = row.get_text().upper()
            cols = row.find_all('td')
            if len(cols) >= 3:
                buy = cols[1].get_text(strip=True).split()[0]
                sale = cols[2].get_text(strip=True).split()[0]
                if "USD" in txt:
                    res["usd"] = f"{buy} / {sale}"
                    res["u_val"] = float(buy.replace(',', '.'))
                elif "EUR" in txt:
                    res["eur"] = f"{buy} / {sale}"
                    res["e_val"] = float(buy.replace(',', '.'))
    return res

def parse_fuel():
    """Ціни на пальне з finance.i.ua"""
    soup = get_soup("https://finance.i.ua/fuel/")
    fuel = {"a95": "н/д", "dp": "н/д", "gas": "н/д"}
    if not soup: return fuel
    
    # Шукаємо таблицю середніх цін (остання таблиця на сторінці зазвичай містить середні)
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            if "Середня" in row.get_text():
                cols = row.find_all('td')
                if len(cols) >= 4:
                    fuel["a95"] = cols[2].get_text(strip=True)
                    fuel["dp"] = cols[3].get_text(strip=True)
                    # Газ зазвичай в наступній колонці або рядку, finance.i.ua має свою специфіку
                    # Якщо точна середня не знайдена, беремо перші значення А-95 та ДП
    return fuel

def get_git_info(file, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if key.lower() in line.lower():
                    return line.split('—')[-1].strip() if '—' in line else line.strip()
    except: pass
    return "дані відсутні"

def send():
    c = parse_currency()
    f = parse_fuel()
    now = datetime.now()
    
    cross = round(c['e_val'] / c['u_val'], 3) if c['u_val'] > 0 else "н/д"
    m_ukr = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_ukr[now.month-1]}" # "27 лютого"
    day_hist = now.strftime("%m-%d")            # "02-27"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс валют (finance.i.ua):**\n🇺🇸 USD: {c['usd']}\n🇪🇺 EUR: {c['eur']}\n💱 Крос-курс: {cross}\n\n"
        f"⛽ **Пальне (i.ua):**\n🔹 А-95: {f['a95']} грн\n🔹 ДП: {f['dp']} грн\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_name)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', day_hist)}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
