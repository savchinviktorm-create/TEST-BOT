import os
import urllib.request
import json
from datetime import datetime

# СЮДИ ВСТАВ СВОЄ ПОСИЛАННЯ (CSV)
URL_CURRENCY_TABLE = "ТВОЄ_ПОСИЛАННЯ_З_КРОКУ_ПУБЛІКАЦІЇ"

def get_raw_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_currency():
    raw_data = get_raw_data(URL_CURRENCY_TABLE)
    if not raw_data:
        return "❌ Дані валют недоступні"
    
    lines = [line.split(',') for line in raw_data.splitlines() if line.strip()]
    
    try:
        def clean(val):
            return val.replace('"', '').strip()

        # Шукаємо потрібні рядки за ключовими словами, щоб не залежати від номерів рядків
        usd_buy, usd_sale = "?", "?"
        eur_buy, eur_sale = "?", "?"
        black_usd_buy, black_usd_sale = "?", "?"

        for row in lines:
            if len(row) > 2 and clean(row[0]) == "USD":
                usd_buy, usd_sale = clean(row[1]), clean(row[2])
                if len(row) > 6: # Чорний ринок зазвичай праворуч
                    black_usd_buy, black_usd_sale = clean(row[5]), clean(row[6])
            if len(row) > 2 and clean(row[0]) == "EUR":
                eur_buy, eur_sale = clean(row[1]), clean(row[2])

        # Розрахунок крос-курсу в коді
        try:
            cross = round(float(eur_buy) / float(usd_buy), 3)
        except:
            cross = "немає даних"

        return (
            f"🇺🇸 **USD:** Банки: {usd_buy}/{usd_sale} | Обмін: {black_usd_buy}/{black_usd_sale}\n"
            f"🇪🇺 **EUR:** Банки: {eur_buy}/{eur_sale}\n"
            f"💱 **Крос-курс EUR/USD:** {cross}"
        )
    except Exception as e:
        return f"⚠️ Дані оновлюються в таблиці..."

def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    locs = [("Головецько", "lat=49.20&lon=23.45"), ("Львів", "q=Lviv")]
    reports = []
    for name, p in locs:
        url = f"http://api.openweathermap.org/data/2.5/weather?{p}&appid={api_key}&units=metric&lang=uk"
        d = get_raw_data(url)
        if d:
            js = json.loads(d)
            temp = round(js['main']['temp'])
            desc = js['weather'][0]['description'].capitalize()
            reports.append(f"📍 {name}: {temp}°C, {desc}")
    return "\n".join(reports)

def send_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    now = datetime.now()
    
    months = ["січня", "лютого", "березня", "квітня", "травня", "червня", "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]
    history_url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/history.txt"
    names_url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/names.txt"
    
    def get_git(url, key):
        d = get_raw_data(url)
        if d:
            for l in d.splitlines():
                if key in l: return l.split(':', 1)[-1].strip() if ':' in l else l.split('—', 1)[-1].strip()
        return "немає даних"

    msg = (
        f"📅 **РАНКОВИЙ ЗВІТ ({now.strftime('%d.%m.%Y')})**\n\n"
        f"🌡 **Погода:**\n{get_weather()}\n\n"
        f"💰 **Курс валют (Мінфін):**\n{parse_currency()}\n\n"
        f"😇 **Іменини:**\n{now.strftime('%d.%m')}: {get_git(names_url, f'{now.day} {months[now.month-1]}')}\n\n"
        f"📜 **Історія:**\n{get_git(history_url, now.strftime('%m-%d'))}\n\n"
        f"✨ **Гороскоп:**\n"
        f"♈ Овен: Будьте обережні з фінансами.\n♉ Телець: Зосередьтесь на головному.\n"
        f"♊ Близнюки: Час для відпочинку.\n♋ Рак: Слухайте інтуїцію.\n"
        f"♌ Лев: Вдалий день для починань.\n♍ Діва: Зверніть увагу на деталі.\n"
        f"♎ Терези: Гармонія у всьому.\n♏ Скорпіон: Енергійний день.\n"
        f"♐ Стрілець: Нові можливості.\n♑ Козоріг: Стійкість принесе успіх.\n"
        f"♒ Водолій: Час для креативу.\n♓ Риби: День для роздумів.\n\n"
        f"💡 **Цитата дня:**\n\"Хтось сидить у тіні сьогодні, тому що хтось давно посадив дерево.\" (Воррен Баффет)\n\n"
        f"😂 **Анекдот:**\n— Василю Івановичу, поїхали до міста, там виставка голографії йде!\n— Ні, Петько, на біса мені на голих графів дивитися?\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів!\n\n"
        f"⛽ **Ціни на пальне:**\nА-95: 56.15 грн\nДП: 52.30 грн\nГаз: 27.85 грн"
    )

    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", 
                                 data=json.dumps({"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

if __name__ == "__main__":
    send_report()
