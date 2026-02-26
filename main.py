import logging
import asyncio
import requests
import datetime
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
# Додаємо бібліотеку для розкладу
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MY_CHAT_ID = os.getenv("MY_CHAT_ID") # Додайте свій ID у змінні Render

LOCATIONS = {
    "с. Головецько": {"lat": 49.1972, "lon": 23.4683},
    "м. Львів": {"lat": 49.8397, "lon": 24.0297}
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Ті ж самі функції отримання даних (без змін) ---
def get_weather(city_name, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("cod") != 200: return f"❌ {city_name}: Помилка API (можливо, ключ ще не активний)"
        temp = round(res['main']['temp'])
        desc = res['weather'][0]['description'].capitalize()
        return f"🌡 {city_name}: {'+' if temp > 0 else ''}{temp}°C, {desc}"
    except: return f"❌ {city_name}: Недоступно"

def get_currency():
    url = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
    try:
        res = requests.get(url).json()
        usd = next(item for item in res if item["ccy"] == "USD")
        eur = next(item for item in res if item["ccy"] == "EUR")
        return f"💵 **Курс:** USD: {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | EUR: {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except: return "❌ Курс недоступний"

def get_data_by_date(filename, current_date):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(current_date): return line.split(':', 1)[1].strip()
    except: return None
    return None

def get_random_line(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return random.choice(lines)
    except: return "Дані відсутні"

# --- Функція формування звіту ---
async def build_report():
    now = datetime.datetime.now()
    mm_dd = now.strftime("%m-%d")
    w_gol = get_weather("с. Головецько", LOCATIONS["с. Головецько"]["lat"], LOCATIONS["с. Головецько"]["lon"])
    w_lviv = get_weather("м. Львів", LOCATIONS["м. Львів"]["lat"], LOCATIONS["м. Львів"]["lon"])
    
    return (
        f"📅 **Сьогодні: {now.strftime('%d.%m.%Y')}**\n\n"
        f"🌈 **ПОГОДА:**\n{w_gol}\n{w_lviv}\n\n"
        f"{get_currency()}\n\n"
        f"⏳ **ЦЕЙ ДЕНЬ В ІСТОРІЇ:**\n{get_data_by_date('history.txt', mm_dd) or 'Немає подій'}\n\n"
        f"😇 **ІМЕНИНИ:**\n{get_data_by_date('names.txt', mm_dd) or 'Немає'}\n\n"
        f"💡 **ЦИТАТА:**\n_{get_random_line('database.txt')}_\n\n"
        f"😂 **АНЕКДОТ:**\n{get_random_line('jokes.txt')}"
    )

# --- Автоматична відправка ---
async def daily_job():
    if MY_CHAT_ID:
        report = await build_report()
        await bot.send_message(chat_id=MY_CHAT_ID, text=report, parse_mode="Markdown")

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(f"Привіт! Твій ID: `{message.chat.id}`\nЗбережи його в налаштування Render як MY_CHAT_ID для авто-повідомлень.", parse_mode="Markdown")

@dp.message(lambda message: message.text == "☀️ Отримати ранковий звіт")
async def manual_report(message: types.Message):
    report = await build_report()
    await message.answer(report, parse_mode="Markdown")

async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    # Встановіть час (наприклад, 08:00)
    scheduler.add_job(daily_job, 'cron', hour=8, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
