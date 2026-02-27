import os
import urllib.request
import json
from datetime import datetime

# --- ВСТАВ СВОЄ ПОСИЛАННЯ (CSV) ТУТ ---
URL_CURRENCY_TABLE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSExxHF9GN-lpJF9I3L9kLzFoH9lo4_emwtiEoHpiezlf3ESOw6dxGrjmQwk1wuFC6mV6035wu6-l4M/pub?gid=2060076239&single=true&output=csv"

def get_raw_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except:
        return None

def parse_currency():
    data = get_raw_data(URL_CURRENCY_TABLE)
    if not data:
        return "❌ Не вдалося завантажити дані з таблиці"
    
    # Розбиваємо таблицю на рядки та елементи
    lines = [line.split(',') for line in data.splitlines()]
    
    usd_bank = "немає даних"
    eur_bank = "немає даних"
    usd_black = "немає даних"
    eur_black = "немає даних"
    
    def clean(val):
        return val.replace('"', '').strip()

    try:
        for row in lines:
            if len(row) < 2: continue
            
            # Шукаємо USD у першому стовпці (Банки)
            if clean(row[0]) == "USD":
                usd_bank = f"{clean(row[1])} / {clean(row[2])}"
                # Якщо в цьому ж рядку є дані обмінників (стовпці F, G)
                if len(row) > 6 and clean(row[5]) != "":
                    usd_black = f"{clean(row[5])} / {clean(row[6])}"
            
            # Шукаємо EUR у першому стовпці (Банки)
            if clean(row[0]) == "EUR":
                eur_bank = f"{clean(row[1])} / {clean(row[2])}"
                # Якщо в наступних стовпцях є євро обмінників
                if len(row) > 6 and clean(row[5]) != "":
                    eur_black = f"{clean(row[5])} / {clean(row[6])}"

        # Рахуємо крос-курс прямо тут (EUR купівля / USD купівля)
        try:
            e_val = float(eur_bank.split('/')[0].replace(',', '.').strip())
            u_val = float(usd_bank.split('/')[0].replace(',', '.').strip())
            cross = round(e_val / u_val, 3)
        except:
            cross = "не розраховано"

        return (
            f"🇺🇸 **USD:** Банки: {usd_bank} | Обмін: {usd_black}\n"
            f"🇪🇺 **EUR:** Банки: {eur_bank} | Обмін: {eur_black}\n"
            f"💱 **Крос-курс EUR/USD:** {cross}"
        )
    except:
        return "⚠️ Помилка обробки структури таблиці"

def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    locs = [("Головецько", "lat=49.20&lon=23.45"), ("Львів", "q=Lviv")]
    reports = []
    for name, p in locs:
        url = f"http://api.openweathermap.org/data/2.5/weather?{p}&appid={api_key}&units=metric&lang=uk"
        d = get_raw_data(url)
        if d:
            js = json.loads(d)
            reports.append(f"📍 {name}: {round(js['main']['temp'])}°C, {js['weather'][0]['description'].capitalize()}")
    return "\n".join(reports)

def send_report():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('MY_CHAT_ID')
    now = datetime.now()
    
    # Дані з GitHub файлів (іменини, історія)
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
