import os
import json
import random
import urllib.request
import urllib.parse
import re
from datetime import datetime

def get_fuel_prices():
    try:
        # Використовуємо Мінфін для отримання цін ОККО
        url = "https://index.minfin.com.ua/ua/markets/fuel/tm/okko/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as f:
            html = f.read().decode('utf-8')
            
            def find_p(name):
                # Пошук ціни в таблиці
                match = re.search(fr'{name}.*?([\d.,]+)', html, re.IGNORECASE | re.DOTALL)
                return match.group(1).replace(',', '.') if match else "—"

            return (f"⛽ <b>Ціни ОККО (Мінфін):</b>\n"
                    f"🔹 А-95+: {find_p('А-95')} грн\n"
                    f"🔹 ДП: {find_p('Дизель')} грн\n"
                    f"🔹 ГАЗ: {find_p('Газ')} грн")
    except:
        return "⛽ <b>Ціни ОККО:</b> тимчасово недоступні"

def get_weather(city, lat, lon, key):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=uk"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description'].capitalize()
            return f"📍 {city}: {'+' if temp > 0 else ''}{temp}°C, {desc}"
    except:
        return f"📍 {city}: дані недоступні"

def get_mono_currency():
    try:
        url = "https://api.monobank.ua/bank/currency"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            usd = next(item for item in data if item['currencyCodeA'] == 840 and item['currencyCodeB'] == 980)
            eur = next(item for item in data if item['currencyCodeA'] == 978 and item['currencyCodeB'] == 980)
            return f"🔹 <b>Mono:</b> USD {usd['rateBuy']}/{usd['rateSell']} | EUR {eur['rateBuy']}/{eur['rateSell']}"
    except:
        return "🔹 <b>Mono:</b> недоступний"

def get_privat_currency():
    try:
        url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
        with urllib.request.urlopen(url, timeout=10) as f:
            data = json.loads(f.read().decode())
            usd = next(item for item in data if item['ccy'] == 'USD')
            eur = next(item for item in data if item['ccy'] == 'EUR')
            return f"🔸 <b>Приват:</b> USD {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | EUR {float(eur['buy']):.2f}/{float(eur['sale']):.2f}"
    except:
        return "🔸 <b>Приват:</b> недоступний"

def get_horoscope():
    try:
        signs = {"Овен":"♈","Телець":"♉","Близнюки":"♊","Рак":"♋","Лев":"♌","Діва":"♍","Терези":"♎","Скорпіон":"♏","Стрілець":"♐","Козоріг":"♑","Водолій":"♒","Риби":"♓"}
        advices = ["Вдалий день для нових починань.", "Будьте обережні з фінансами.", "День сприяє спілкуванню.", "Сприятливий час для відпочинку.", "Ваші лідерські якості на висоті.", "Зверніть увагу на здоров'я."]
        text = "<b>✨ Гороскоп на сьогодні:</b>\n"
        for s, e in signs.items():
            text += f"{e} {s}: {random.choice(advices)}\n"
        return text
    except:
        return "✨ Гороскоп: недоступний"

def get_line_by_date(file_name, default_msg):
    today = datetime.now().strftime('%d.%m')
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(today):
                    return line.strip()
    return f"{today}: {default_msg}"

def get_random_line(file_name, default_text):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            return random.choice(lines) if lines else default_text
    return default_text

def send_telegram(token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=15) as f:
            return True
    except:
        return False

if __name__ == "__main__":
    TOKEN = os.environ.get("TOKEN", "").strip()
    CHAT_ID = os.environ.get("MY_CHAT_ID", "").strip()
    W_KEY = os.environ.get("WEATHER_API_KEY", "").strip()

    # Розрахунок часу (Київ)
    now_hour = (datetime.now().hour + 2) % 24
    date_str = datetime.now().strftime('%d.%m.%Y')
    
    weather_info = [
        get_weather("Головецько", 49.19, 23.46, W_KEY),
        get_weather("Львів", 49.83, 24.02, W_KEY)
    ]
    
    currency_info = [
        "💰 <b>Курс валют для порівняння:</b>",
        get_mono_currency(),
        get_privat_currency()
    ]

    if now_hour >= 14:
        # --- ДЕННИЙ ОГЛЯД ---
        report = [
            f"🌤 <b>ДЕННИЙ ОГЛЯД ({date_str})</b>\n",
            *weather_info,
            "\n" + "\n".join(currency_info),
            "\n" + get_fuel_prices(),
            "\n<i>Гарного вечора! ✅</i>"
        ]
    else:
        # --- РАНКОВИЙ ЗВІТ ---
        days_left = (datetime(datetime.now().year + 1, 1, 1) - datetime.now()).days
        report = [
            f"📅 <b>РАНКОВИЙ ЗВІТ ({date_str})</b>\n",
            *weather_info,
            "\n" + "\n".join(currency_info) + "\n",
            "😇 <b>Іменини сьогодні:</b>",
            get_line_by_date("names.txt", "немає даних про іменини"),
            "\n📜 <b>Цей день в історії:</b>",
            get_line_by_date("history.txt", "сьогодні спокійний день"),
            "\n" + get_horoscope(),
            "\n💡 <b>Цитата дня:</b>",
            f"<i>\"{get_random_line('database.txt', 'Живи сьогодні!')}\"</i>",
            "\n😂 <b>Анекдот дня:</b>",
            get_random_line("jokes.txt", "сьогодні без жартів..."),
            f"\n🎄 До Нового року залишилося: <b>{days_left}</b> днів!",
            "\n<i>Вдалого дня! ✅</i>"
        ]

    send_telegram(TOKEN, CHAT_ID, "\n".join(report))
