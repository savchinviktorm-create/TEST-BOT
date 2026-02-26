import logging
import asyncio
import requests
import datetime
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# ==========================================
# 1. НАЛАШТУВАННЯ (ВСТАВ СВОЇ ДАНІ)
# ==========================================
TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
WEATHER_API_KEY = "5b36494556f68d2d8e409158d9c49c0c"

# Координати для точного прогнозу
LOCATIONS = {
    "Головецько": {"lat": 49.1972, "lon": 23.4683},
    "Львів": {"lat": 49.8397, "lon": 24.0297}
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ==========================================
# 2. ДОПОМІЖНІ ФУНКЦІЇ
# ==========================================

def get_weather(city_name, lat, lon):
    """Отримує погоду через OpenWeatherMap API"""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        res = requests.get(url, timeout=10).json()
        temp = round(res['main']['temp'])
        desc = res['weather'][0]['description'].capitalize()
        return f"🌡 {city_name}: {temp}°C, {desc}"
    except Exception:
        return f"❌ Погода для {city_name} тимчасово недоступна"

def get_currency():
    """Отримує курс валют з API ПриватБанку"""
    url = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
    try:
        res = requests.get(url, timeout=10).json()
        usd = next(item for item in res if item["ccy"] == "USD")
        eur = next(item for item in res if item["ccy"] == "EUR")
        return (f"💵 **Курс валют (ПриватБанк):**\n"
                f"🇺🇸 USD: {float(usd['buy']):.2f} / {float(usd['sale']):.2f}\n"
                f"🇪🇺 EUR: {float(eur['buy']):.2f} / {float(eur['sale']):.2f}")
    except Exception:
        return "❌ Курс валют зараз недоступний"

def get_data_by_date(filename, current_date):
    """Шукає рядок, що починається на 'MM-DD:' (напр. '02-26:')"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(current_date):
                    # Повертаємо текст після двокрапки
                    return line.split(':', 1)[1].strip()
    except FileNotFoundError:
        return f"Помилка: файл {filename} не знайдено."
    return None

def get_random_line(filename):
    """Повертає випадковий рядок з файлу (для анекдотів та цитат)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
            return random.choice(lines) if lines else "Дані відсутні."
    except FileNotFoundError:
        return f"Помилка: файл {filename} не знайдено."

# ==========================================
# 3. ЛОГІКА ТЕЛЕГРАМ-БОТА
# ==========================================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    """Створює головне меню з кнопкою"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="☀️ Отримати ранковий звіт")
    await message.answer(
        f"Вітаю, {message.from_user.first_name}! 👋\n"
        "Я готовий надати тобі актуальну інформацію на сьогодні.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(lambda message: message.text == "☀️ Отримати ранковий звіт")
async def send_report(message: types.Message):
    """Збирає всі дані до купи та відправляє користувачу"""
    now = datetime.datetime.now()
    mm_dd = now.strftime("%m-%d")  # Ключ для пошуку у файлах (напр. 02-26)
    pretty_date = now.strftime("%d.%m.%Y")

    # Отримуємо всі частини звіту
    weather_gol = get_weather("с. Головецько", LOCATIONS["Головецько"]["lat"], LOCATIONS["Головецько"]["lon"])
    weather_lviv = get_weather("м. Львів", LOCATIONS["Львів"]["lat"], LOCATIONS["Львів"]["lon"])
    currency = get_currency()
    
    # Контент за датою (строго хронологічно)
    history_fact = get_data_by_date("history.txt", mm_dd) or "На цей день подій в базі немає."
    names_day = get_data_by_date("names.txt", mm_dd) or "На сьогодні іменин не знайдено."
    
    # Контент випадковий
    joke = get_random_line("jokes.txt")
    quote = get_random_line("database.txt")

    # Формуємо фінальний текст
    report = (
        f"📅 **Сьогодні: {pretty_date}**\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🌈 **ПОГОДА:**\n{weather_gol}\n{weather_lviv}\n\n"
        f"{currency}\n\n"
        f"⏳ **ЦЕЙ ДЕНЬ В ІСТОРІЇ:**\n{history_fact}\n\n"
        f"😇 **ІМЕНИНИ:**\n{names_day}\n\n"
        f"💡 **ЦИТАТА ДНЯ:**\n_{quote}_\n\n"
        f"😂 **АНЕКДОТ:**\n{joke}"
    )

    await message.answer(report, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот вимкнений")
