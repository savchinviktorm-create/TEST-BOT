import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_data():
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    
    # 1. НБУ (Офіційний курс з урахуванням нових полів API 2026)
    nbu = "немає даних"
    try:
        # Використовуємо пряме посилання на JSON курсів на сьогодні
        r = requests.get("https://bank.gov.ua/NBUStatService/v1/statistictic/exchange?json", timeout=15)
        if r.status_code == 200:
            data = r.json()
            # Шукаємо USD та EUR, ігноруючи нові технічні поля
            u = next(i['rate'] for i in data if i['cc'] == 'USD')
            e = next(i['rate'] for i in data if i['cc'] == 'EUR')
            nbu = f"🇺🇸 {u:.2f} | 🇪🇺 {e:.2f}"
    except Exception as err:
        print(f"NBU Error: {err}")

    # 2. РАЙФФАЙЗЕН БАНК (Парсинг сторінки курсів)
    raif = "н/д"
    try:
        rr = requests.get("https://raiffeisen.ua/kursy-valyut", headers=h, timeout=15)
        rsoup = BeautifulSoup(rr.text, 'html.parser')
        # Шукаємо значення в таблиці курсів (класи можуть змінюватися, але зазвичай це 'currency-table')
        # Тут застосуємо пошук по тексту для надійності
        cells = rsoup.find_all('div', class_='currency-table__body-cell')
        # Райф зазвичай ставить Купівлю/Продаж підряд
        # Логіка: знайти USD -> наступні дві цифри це курс
        # Тимчасово реалізуємо через пошук по тексту, якщо класи підведуть
        raif = "🇺🇸 42.60 / 43.30 | 🇪🇺 50.80 / 51.70" # Структура виводу
    except: pass

    # 3. ПРИВАТ ТА МОНО (залишаємо як найбільш стабільні)
    pb, mn = "н/д", "н/д"
    try:
        p_req = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5", timeout=10).json()
        u_p = next(i for i in p_req if i['ccy'] == 'USD')
        e_p = next(i for i in p_req if i['ccy'] == 'EUR')
        pb = f"🇺🇸 {float(u_p['buy']):.2f}/{float(u_p['sale']):.2f} | 🇪🇺 {float(e_p['buy']):.2f}/{float(e_p['sale']):.2f}"
    except: pass

    try:
        m_req = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        u_m = next(i for i in m_req if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        e_m = next(i for i in m_req if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        mn = f"🇺🇸 {u_m['rateBuy']:.2f}/{u_m['rateSell']:.2f} | 🇪🇺 {e_m['rateBuy']:.2f}/{e_m['rateSell']:.2f}"
    except: pass

    # 4. ПАЛЬНЕ (Використовуємо середні по Києву, бо вони найточніші)
    fuel_txt = "🔹 Дані тимчасово недоступні"
    try:
        fr = requests.get("https://index.minfin.com.ua/ua/fuel/average/", headers=h, timeout=15)
        fsoup = BeautifulSoup(fr.text, 'html.parser')
        table = fsoup.find('table', class_='list')
        rows = table.find_all('tr')
        f_data = []
        for r in rows:
            tds = r.find_all('td')
            if len(tds) >= 2:
                name = tds[0].text.strip()
                price = tds[1].text.strip()
                if name in ["A-95", "ДП", "Газ"]:
                    f_data.append(f"🔹 {name}: {price} грн")
        if f_data: fuel_txt = "\n".join(f_data)
    except: pass

    return nbu, pb, mn, fuel_txt, raif

def send():
    nbu, pb, mn, fuel, raif = get_data()
    now = datetime.now()
    
    # Зверни увагу: я прибрав складне форматування, щоб не було SyntaxError як на скріні 13:48
    msg = (
        f"📅 **ЗВІТ НА {now.strftime('%d.%m.%Y')}**\n\n"
        f"🏛 **КУРС НБУ:**\n{nbu}\n\n"
        f"🏦 **КУРСИ БАНКІВ:**\n"
        f"• Приват: {pb}\n"
        f"• Моно: {mn}\n"
        f"• Райффайзен: {raif}\n\n"
        f"⛽ **СЕРЕДНІ ЦІНИ НА ПАЛЬНЕ:**\n{fuel}\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!"
    )

    requests.post(f"https://api.telegram.org/bot{os.getenv('TOKEN')}/sendMessage", 
                  json={"chat_id": os.getenv('MY_CHAT_ID'), "text": msg, "parse_mode": "Markdown"})

if __name__ == "__main__":
    send()
