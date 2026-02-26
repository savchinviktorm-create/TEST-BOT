import requests
from bs4 import BeautifulSoup
import telebot
import time
import random

# --- ВСТАВТЕ ВАШІ ДАНІ ---
TOKEN = '8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY'
CHAT_ID = '653398188'

def get_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 1. Погода (Sinoptik) - на Render це ПРАЦЮВАТИМЕ
    try:
        r = requests.get('https://sinoptik.ua/pohoda/holovetsko', headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        t_min = soup.select_one('.temperature .min span').text
        t_max = soup.select_one('.temperature .max span').text
        desc = soup.select_one('.wDescription .description').text.strip()
        weather = f"🌡 **Погода у Головецько:** {t_min}..{t_max}\n{desc}"
    except:
        weather = "⚠️ Погода тимчасово недоступна"

    # 2. Курс валют (ПриватБанк)
    try:
        res = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5', timeout=10).json()
        usd = next(i for i in res if i['ccy'] == 'USD')
        eur = next(i for i in res if i['ccy'] == 'EUR')
        currency = f"💰 **USD:** {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | **EUR:** {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except:
        currency = "⚠️ Курс валют недоступний"

    # 3. Гороскоп (Водолій)
    try:
        r = requests.get('https://goroskop.i.ua/aquarius/', headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        horo = f"♒️ **Водолій:** " + soup.select_one('.description').text.strip().split('.')[0] + "."
    except:
        horo = "♒️ **Водолій:** Сьогодні день сприяє новим починанням!"

    # 4. Мотивація (Українською)
    motivational_quotes = [
        "Твій успіх залежить від твоїх дій сьогодні!",
        "Маленькі кроки ведуть до великих результатів.",
        "Будь кращим за себе вчорашнього.",
        "Кожен день — це нова можливість."
    ]
    motivation = f"✨ **Мотивація:** {random.choice(motivational_quotes)}"

    return f"Доброго ранку! ☀️\n\n{weather}\n\n{currency}\n\n{horo}\n\n{motivation}"

bot = telebot.TeleBot(TOKEN)

# Функція циклу
while True:
    try:
        message_text = get_data()
        bot.send_message(CHAT_ID, message_text, parse_mode='Markdown')
        print("Повідомлення надіслано!")
        time.sleep(86400) # Чекати 24 години
    except Exception as e:
        print(f"Помилка: {e}")
        time.sleep(60)
