import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_currency_data():
    """Парсинг курсу з https://minfin.com.ua/ua/currency/"""
    try:
        url = "https://minfin.com.ua/ua/currency/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Шукаємо таблицю середнього курсу
        table = soup.find('table', class_='mfcur-table-bank')
        rows = table.find_all('tr')
        
        data = {"usd": "н/д", "eur": "н/д", "usd_val": 0, "eur_val": 0}
        
        for row in rows:
            text = row.text.upper()
            cols = row.find_all('td')
            if len(cols) > 1:
                # Очищуємо текст від зайвих пробілів та символів
                val_text = cols[1].text.replace('\xa0', ' ').strip().split()
                if "USD" in text:
                    data["usd"] = f"{val_text[0]} / {val_text[1]}"
                    data["usd_val"] = float(val_text[0].replace(',', '.'))
                elif "EUR" in text:
                    data["eur"] = f"{val_text[0]} / {val_text[1]}"
                    data["eur_val"] = float(val_text[0].replace(',', '.'))
        return data
    except:
        return None

def get_fuel_data():
    """Парсинг пального з https://index.minfin.com.ua/ua/markets/fuel/"""
    try:
        url = "https://index.minfin.com.ua/ua/markets/fuel/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Знаходимо таблицю з середніми цінами
        table = soup.find('table', class_='list')
        rows = table.find_all('tr')
        
        fuel = {"a95": "н/д", "dp": "н/д", "gas": "н/д"}
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                name = cols[0].text.strip()
                price = cols[1].text.strip()
                if name == "A-95": fuel["a95"] = price
                elif name == "ДП": fuel["dp"] = price
                elif name == "Газ": fuel["gas"] = price
        return fuel
    except:
        return None

def get_git_info(file_name, search_key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if search_key.lower() in line.lower():
                    return line.split('—', 1)[-1].strip() if '—' in line else line.strip()
    except: pass
    return "дані відсутні"

def send_report():
    curr = get_currency_data()
    fuel = get_fuel_data()
    now = datetime.now()
    
    # Розрахунок крос-курсу
    cross = round(curr['eur_val'] / curr['usd_val'], 3) if curr and curr['usd_val'] > 0 else "н/д"
    
    # Дата для іменин
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    day_month = f"{now.day} {months[now.month-1]}"

    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"💰 **Курс валют (Мінфін):**\n"
        f"🇺🇸 USD: {curr['usd'] if curr else 'помилка'}\n"
        f"🇪🇺 EUR: {curr['eur'] if curr else 'помилка'}\n"
        f"💱 Крос-курс: {cross}\n\n"
        f"⛽ **Ціни на пальне (Мінфін):**\n"
        f"🔹 А-95: {fuel['a95'] if fuel else 'н/д'} грн\n"
        f"🔹 ДП: {fuel['dp'] if fuel else 'н/д'} грн\n"
        f"🔹 Газ: {fuel['gas'] if fuel else 'н/д'} грн\n\n"
        f"😇 **Іменини сьогодні:**\n{get_git_info('names.txt', day_month)}\n\n"
        f"📜 **Цей день в історії:**\n{get_git_info('history.txt', now.strftime('%m-%d'))}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send_report()
