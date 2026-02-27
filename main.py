import os
import urllib.request
import json
from datetime import datetime

# ---------- УНІВЕРСАЛЬНЕ ОТРИМАННЯ ДАНИХ ----------
def get_data(url):
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except:
        return None

# ---------- ПОГОДА ----------
def get_weather():
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        return "API ключ погоди не заданий"

    locations = [
        {
            "name": "Головецько",
            "url": f"https://api.openweathermap.org/data/2.5/weather?lat=49.20&lon=23.45&appid={api_key}&units=metric&lang=uk"
        },
        {
            "name": "Львів",
            "url": f"https://api.openweathermap.org/data/2.5/weather?q=Lviv&appid={api_key}&units=metric&lang=uk"
        }
    ]

    reports = []

    for loc in locations:
        raw = get_data(loc["url"])
        if not raw:
            continue
        try:
            data = json.loads(raw)
            temp = round(data["main"]["temp"])
            desc = data["weather"][0]["description"].capitalize()
            reports.append(f"📍 {loc['name']}: {temp}°C, {desc}")
        except:
            pass

    return "\n".join(reports) if reports else "Немає даних"

# ---------- КУРС ВАЛЮТ ----------
def get_currency():
    raw = get_data("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
    if not raw:
        return "Немає даних"

    try:
        data = json.loads(raw)
        rates = {c["ccy"]: c for c in data}

        usd = rates["USD"]
        eur = rates["EUR"]

        usd_buy = float(usd["buy"])
        usd_sale = float(usd["sale"])
        eur_buy = float(eur["buy"])
        eur_sale = float(eur["sale"])

        cross = round(usd_sale / eur_sale, 4)

        return (
            f"💵 USD: {usd_buy:.2f}/{usd_sale:.2f}\n"
            f"💶 EUR: {eur_buy:.2f}/{eur_sale:.2f}\n"
            f"🔁 USD/EUR: {cross}"
        )
    except:
        return "Немає даних"

# ---------- ПАЛЬНЕ (як є зараз) ----------
def get_fuel():
    raw = get_data("https://minfin.com.ua/api/fuel/")
    if not raw:
        return "Немає даних"

    try:
        data = json.loads(raw)
        return (
            f"А-95: {data.get('a95', '—')} грн\n"
            f"ДП: {data.get('dp', '—')} грн\n"
            f"Газ: {data.get('gas', '—')} грн"
        )
    except:
        return "Немає даних"

# ---------- ФАЙЛИ З GITHUB ----------
def get_file_info(file_name, search_key):
    url = f"https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/{file_name}"
    data = get_data(url)
    if not data:
        return "немає даних"

    for line in data.splitlines():
        if search_key in line:
            if "—" in line:
                return line.split("—", 1)[-1].strip()
            if ":" in line:
                return line.split(":", 1)[-1].strip()
            return line.strip()

    return "немає даних"

# ---------- ГОЛОВНЕ ПОВІДОМЛЕННЯ ----------
def send_main():
    token = os.getenv("TOKEN")
    chat_id = os.getenv("MY_CHAT_ID")
    if not token or not chat_id:
        return

    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    day_month = now.strftime("%m-%d")

    months_ukr = [
        "січня", "лютого", "березня", "квітня", "травня", "червня",
        "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"
    ]
    name_search = f"{now.day} {months_ukr[now.month - 1]}"

    history = get_file_info("history.txt", day_month)
    namenay = get_file_info("names.txt", name_search)

    # --- умовний блок іменин ---
    name_block = ""
    if namenay != "немає даних":
        name_block = f"😇 *Іменини:*\n{namenay}\n\n"

    message = (
        f"📅 *РАНКОВИЙ ЗВІТ ({date_str})*\n\n"
        f"🌡 *Погода:*\n{get_weather()}\n\n"
        f"💰 *Курс валют:*\n{get_currency()}\n\n"
        f"⛽️ *Ціни на пальне:*\n{get_fuel()}\n\n"
        f"{name_block}"
        f"📜 *Історія дня:*\n{history}\n\n"
        f"💡 *Цитата дня:*\n"
        f"\"Хтось сидить у тіні сьогодні, тому що хтось давно посадив дерево.\" — Воррен Баффет\n\n"
        f"🎄 До Нового року: {(datetime(now.year + 1, 1, 1) - now).days} днів"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )

    urllib.request.urlopen(req)

# ---------- СТАРТ ----------
if __name__ == "__main__":
    send_main()
