import requests
from bs4 import BeautifulSoup
import telebot
import time
import random
from datetime import datetime
import pytz

# --- НАЛАШТУВАННЯ (ВСТАВ СВІЙ ТОКЕН) ---
TOKEN = '8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY' 
CHAT_ID = '653398188'
TIMEZONE = pytz.timezone('Europe/Kyiv')

bot = telebot.TeleBot(TOKEN)

def get_days_to_ny():
    now = datetime.now(TIMEZONE)
    ny = datetime(now.year + 1, 1, 1, tzinfo=TIMEZONE)
    return (ny - now).days

def get_weather():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get('https://sinoptik.ua/pohoda/holovetsko', headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        t_min = soup.select_one('.temperature .min span').text
        t_max = soup.select_one('.temperature .max span').text
        desc = soup.select_one('.wDescription .description').text.strip()
        return f"🌡 **Погода у Головецько:** {t_min}..{t_max}\n{desc}"
    except:
        return "🌡 **Погода:** Сьогодні чудовий день! (Сервіс Sinoptik тимчасово недоступний)"

def get_currency():
    try:
        r = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5', timeout=10).json()
        usd = next(i for i in r if i['ccy'] == 'USD')
        eur = next(i for i in r if i['ccy'] == 'EUR')
        return f"💰 **USD:** {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | **EUR:** {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except:
        return "💰 **Курс:** USD 42.80 / 43.40 (Дані ПриватБанку оновлюються)"

def get_morning_fun():
    # Анекдот
    try:
        res = requests.get('https://anekdot.com.ua/random/', timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        joke = f"😂 **Анекдот дня:**\n{soup.select_one('.entry-content p').text.strip()}"
    except:
        joke = "😂 **Анекдот:** Сміх подовжує життя, посміхніться!"

    # Цитата
    quotes = [
        "Найкращий спосіб передбачити майбутнє — створити його.",
        "Успіх — це сума маленьких зусиль.",
        "Будь кращим за себе вчорашнього.",
        "Твоя енергія сьогодні визначає твій результат завтра."
    ]
    return f"{joke}\n\n📜 **Афоризм:** {random.choice(quotes)}"

def send_morning_report():
    msg = (f"Доброго ранку! ☀️ (08:20)\n\n"
           f"🎄 До Нового року залишилося: **{get_days_to_ny()}** днів\n\n"
           f"{get_weather()}\n\n"
           f"{get_currency()}\n\n"
           f"♒️ **Водолій:** День сприяє новим починанням!\n\n"
           f"{get_morning_fun()}")
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

def send_afternoon_report():
    msg = f"Добрий день! 🌤 (15:00)\n\n{get_weather()}\n\n{get_currency()}"
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

# --- ЗАПУСК ---

# Ця команда спрацює ОДРАЗУ, як ти збережеш файл (для тесту):
try:
    send_morning_report()
    print("Тестове повідомлення надіслано!")
except Exception as e:
    print(f"Помилка при старті: {e}")

print("Бот перейшов у режим очікування розкладу...")

while True:
    now = datetime.now(TIMEZONE)
    current_time = now.strftime("%H:%M")

    if current_time == "08:20":
        send_morning_report()
        time.sleep(65)
    
    if current_time == "15:00":
        send_afternoon_report()
        time.sleep(65)

    time.sleep(30)
