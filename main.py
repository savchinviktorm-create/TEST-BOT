import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_soup(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        return BeautifulSoup(r.text, 'html.parser')
    except: return None

def parse_data():
    # 1. ВАЛЮТИ
    res = {"usd": "н/д", "eur": "н/д", "u_val": 0.0, "e_val": 0.0}
    soup_curr = get_soup("https://finance.i.ua/")
    if soup_curr:
        # Шукаємо саме головну таблицю "Середній курс валют у банках"
        table = soup_curr.find('table', class_='table-delta')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # Витягуємо тільки чистий текст курсу з тегів <span>
                    # cols[1] - Купівля, cols[2] - Продаж
                    buy_span = cols[1].find('span', class_='value')
                    sell_span = cols[2].find('span', class_='value')
                    
                    if buy_span and sell_span:
                        buy = buy_span.get_text(strip=True).replace(',', '.')
                        sell = sell_span.get_text(strip=True).replace(',', '.')
                        
                        currency_name = cols[0].get_text().upper()
                        if "USD" in currency_name:
                            res["usd"] = f"{buy} / {sell}"
                            res["u_val"] = float(buy)
                        elif "EUR" in currency_name:
                            res["eur"] = f"{buy} / {sell}"
                            res["e_val"] = float(buy)

    # 2. ПАЛЬНЕ
    fuel = {"a95": "н/д", "dp": "н/д", "gas": "н/д"}
    soup_fuel = get_soup("https://finance.i.ua/fuel/")
    if soup_fuel:
        # Шукаємо рядок "Середня"
        for row in soup_fuel.find_all('tr'):
            txt = row.get_text()
            cells = row.find_all('td')
            if "Середня" in txt and len(cells) >= 4:
                fuel["a95"] = cells[2].get_text(strip=True)
                fuel["dp"] = cells[3].get_text(strip=True)
            # Окремо шукаємо ціну на Газ
            if "Газ" in txt and len(cells) >= 2 and fuel["gas"] == "н/д":
                fuel["gas"] = cells[1].get_text(strip=True)
                
    return res, fuel

def get_git_info(file, key):
    # Пряме посилання на файли у твоєму репозиторії
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lines = r.text.splitlines()
            for line in lines:
                if key in line:
                    return line.split('—', 1)[-1].strip() if '—' in line else line.strip()
    except: pass
    return "дані відсутні"

def send():
    curr, fuel = parse_data()
    now = datetime.now()
    
    # Крос-курс (Купівля EUR / Купівля USD)
    cross = round(curr['e_val'] / curr['u_val'], 2) if curr['u_val'] > 0 else "н/д"
    
    # Назви місяців для іменин
    m_list = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_name = f"{now.day} {m_list[now.month-1]}"
    day_hist = now.strftime("%m-%d")

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс (finance.i.ua):**\n🇺🇸 USD: {curr['usd']}\n🇪🇺 EUR: {curr['eur']}\n💱 Крос-курс: {cross}\n\n"
        f"⛽ **Середні ціни на пальне:**\n🔹 А-95: {fuel['a95']} грн\n🔹 ДП: {fuel
