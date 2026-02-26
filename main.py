import requests
import telebot
import time
import random
from datetime import datetime
import pytz
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- НАЛАШТУВАННЯ ---
TOKEN = '8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY' 
CHAT_ID = '653398188'
TIMEZONE = pytz.timezone('Europe/Kyiv')

bot = telebot.TeleBot(TOKEN)

# --- МІНІ-СЕРВЕР ДЛЯ RENDER (ЩОБ БОТ НЕ СПАВ) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and kicking!")

def run_health_check():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

Thread(target=run_health_check, daemon=True).start()

# --- ФУНКЦІЇ ДЛЯ ОТРИМАННЯ ДАНИХ ---

def get_weather():
    try:
        # Координати с. Головецько
        url = "https://api.open-meteo.com/v1/forecast?latitude=48.93&longitude=23.45&current_weather=true&timezone=Europe%2FKyiv"
        res = requests.get(url, timeout=10).json()
        temp = res['current_weather']['temperature']
        # Додамо опис стану погоди (спрощено)
        return f"🌡 **Погода у Головецько:** {temp}°C"
    except:
        return "🌡 **Погода:** Дані тимчасово недоступні"

def get_currency():
    try:
        # Отримуємо курс ПриватБанку (готівковий)
        res = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5', timeout=10).json()
        usd = next(i for i in res if i['ccy'] == 'USD')
        eur = next(i for i in res if i['ccy'] == 'EUR')
        return (f"💰 **Курс (ПриватБанк):**\n"
                f"💵 USD: {float(usd['buy']):.2f} / {float(usd['sale']):.2f}\n"
                f"💶 EUR: {float(eur['buy']):.2f} / {float(eur['sale']):.2f}")
    except:
        return "💰 **Курс валют:** Сервіс банку не відповідає"

def get_days_to_ny():
    now = datetime.now(TIMEZONE)
    ny = datetime(now.year + (1 if now.month == 12 and now.day > 31 else 0), 1, 1, tzinfo=TIMEZONE)
    # Якщо сьогодні вже 1 січня, рахуємо до наступного року
    if now.month == 1 and now.day == 1:
         ny = datetime(now.year + 1, 1, 1, tzinfo=TIMEZONE)
    delta = ny - now
    return delta.days

def send_full_report(time_label):
    weather = get_weather()
    currency = get_currency()
    days = get_days_to_ny()
    
    jokes = [
        "— Куме, а що ви будете робити на Новий Рік?\n— Та як завжди, обличчям в олів'є!",
        "Оптиміст вірить, що наступний рік буде кращим. Реаліст просто купив генератор.",
        "Ранок у Головецько: пташки співають, курс долара стабільний, але високий.",
        "Діалог у Карпатах:\n— Скільки коштує цей котедж?\n— П'ять тисяч.\n— А чого так дорого?\n— Бо повітря свіже, а ви його задарма дихаєте!"
    ]
    
    quotes = [
        "Найкращий спосіб передбачити майбутнє — створити його.",
        "Дійте так, наче невдача неможлива.",
        "Маленькі кроки сьогодні — великі результати завтра.",
        "Все починається з мрії."
    ]

    msg = (f"Доброго ранку! ☀️ ({time_label})\n\n"
           f"🎄 До Нового року: **{days}** днів\n\n"
           f"{weather}\n\n"
           f"{currency}\n\n"
           f"♒️ **Водолій:** День сприяє фінансовим успіхам та гарному настрою!\n\n"
           f"😂 **Анекдот:**\n{random.choice(jokes)}\n\n"
           f"📜 **Цитата:** {random.choice(quotes)}")
    
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

def send_short_report(time_label):
    weather = get_weather()
    currency = get_currency()
    msg = f"🌤 **Обідній звіт ({time_label}):**\n\n{weather}\n\n{currency}"
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

# --- ЗАПУСК ---

# Відправити відразу при старті для перевірки
try:
    send_full_report("Тестовий запуск")
except Exception as e:
    print(f"Помилка: {e}")

while True:
    now = datetime.now(TIMEZONE)
    current_time = now.strftime("%H:%M")

    # Ранковий звіт о 08:20
    if current_time == "08:20":
        send_full_report("08:20")
        time.sleep(65)
    
    # Обідній звіт о 15:00
    if current_time == "15:00":
        send_short_report("15:00")
        time.sleep(65)

    time.sleep(30)
