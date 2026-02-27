import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_data():
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    
    # 1. НБУ
    nbu = "немає даних"
    try:
        r = requests.get("https://bank.gov.ua/NBUStatService/v1/statistictic/exchange?json", timeout=15)
        if r.status_code == 200:
            d = r.json()
            u = next(i['rate'] for i in d if i['cc'] == 'USD')
            e = next(i['rate'] for i in d if i['cc'] == 'EUR')
            nbu = f"🇺🇸 {u:.2f} | 🇪🇺 {e:.2f}"
    except: pass

    # 2. ПРИВАТ ТА МОНО (через стабільні API)
    pb, mn = "н/д", "н/д"
    try:
        p_req = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5", timeout=10).json()
        u = next(i for i in p_req if i['ccy'] == 'USD')
        e = next(i for i in p_req if i['ccy'] == 'EUR')
        pb = f"🇺🇸 {float(u['buy']):.2f}/{float(u['sale']):.2f} | 🇪🇺 {float(e['buy']):.2f}/{float(e['sale']):.2f}"
    except: pass

    try:
        m_req = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        u = next(i for i in m_req if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        e = next(i for i in m_req if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        mn = f"🇺🇸 {u['rateBuy']:.2f}/{u['rateSell']:.2f} | 🇪🇺 {e['rateBuy']:.2f}/{e['rateSell']:.2f}"
    except: pass

    # 3. ПАЛЬНЕ (спрощений парсинг з vsetutpl.com - там легка таблиця)
    fuel_list = []
    try:
        fr = requests.get("https://vsetutpl.com/uk/tsiny-na-palne-v-ukrayini", headers=h, timeout=15)
        fsoup = BeautifulSoup(fr.text, 'html.parser')
        # Беремо першу ж таблицю на сторінці
        rows = fsoup.find_all('tr')
        for row in rows:
            if "A-95" in row.text or "ДП" in row.text or "Газ" in row.text:
                tds = row.find_all('td')
                if len(tds) >= 2:
                    fuel_list.append(f"{tds[0].text.strip()}: {tds[1].text.strip()} грн")
    except: pass
    
    fuel_txt = "\n".join(fuel_list) if fuel_list else "🔹 Дані тимчасово недоступні"

    return nbu, pb, mn, fuel_txt

def get_git_info(file, key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for line in r.content.decode('utf-8').splitlines():
                if key in line: return line.split('—', -1)[-1].strip()
    except: pass
    return "немає даних"

def send():
    nbu, pb, mn, fuel = get_data()
    now = datetime.now()
    m_ukr = ["січня","лютого","березня","квітня","травня","червня","липня","серпня","вересня","жовтня","листопада","грудня"]
    day_str = f"{now.day} {m_ukr[now.month-1]}"
    
    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"🏛 **КУРС НБУ:**\n{nbu}\n\n"
        f"🏦 **КУРСИ БАНКІВ:**\n• Приват: {pb}\n• Моно: {mn}\n\n"
        f"⛽ **ПАЛЬНЕ (СЕРЕДНІ ЦІНИ):**\n{fuel}\n\n"
        f"😇 **Іменини:** {get_git_info('names.txt', day_str)}\n"
        f"📜 **Історія:** {get_git_info('history.txt', now.strftime('%m-%d'))}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
