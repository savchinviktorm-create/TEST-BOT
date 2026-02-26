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

# --- МІНІ-СЕРВЕР ДЛЯ RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive")

def run_health_check():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

Thread(target=run_health_check, daemon=True).start()

# --- ФУНКЦІЇ ДАНИХ ---
def get_weather():
    try:
        # Координати Головецько
        url = "https://api.open-meteo.com/v1/forecast?latitude=48.93&longitude=23.45&current_weather=true&timezone=Europe%2FKyiv"
        res = requests.get(url, timeout=10).json()
        temp = res['current_weather']['temperature']
        return f"🌡 **Погода у Головецько:** {temp}°C (супутниковий моніторинг)"
    except:
        return "🌡 Погода: Повітря свіже, але датчик трохи підвів."

def get_days_to_ny():
    now = datetime.now(TIMEZONE)
    ny = datetime(now.year + 1, 1, 1, tzinfo=TIMEZONE)
    return (ny - now).days

def send_morning_report():
    weather = get_weather()
    days = get_days_to_ny()
    jokes = [
        "Оптиміст вірить, що 2026-й буде кращим. Реаліст просто купив генератор.",
        "Ранок у Головецько: пташки співають, курс долара стабільний (високий).",
        "— Куме, що ви будете робити на Новий Рік?\n— Та як завжди, обличчям в олів'є!"
    ]
    msg = (f"Доброго ранку! ☀️\n\n"
           f"🎄 До Нового року: **{days}** днів\n\n"
           f"{weather}\n\n"
           f"💰 **Курс:** USD 42.80 / 43.40\n\n"
           f"😂 **Анекдот:**\n{random.choice(jokes)}")
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')

# Тестовий запуск при старті
try:
    send_morning_report()
except:
    pass

while True:
    now = datetime.now(TIMEZONE)
    current_time = now.strftime("%H:%M")

    if current_time == "08:20":
        send_morning_report()
        time.sleep(65)
    
    if current_time == "15:00":
        bot.send_message(CHAT_ID, f"🌤 Обідній звіт:\n\n{get_weather()}")
        time.sleep(65)

    time.sleep(30)
