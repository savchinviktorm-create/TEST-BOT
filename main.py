import requests
import random
import io
from datetime import datetime
import pytz

# --- КОНФІГУРАЦІЯ ---
TOKEN = "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY"
CHAT_ID = "653398188"
GITHUB_BASE = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/"

def get_list_from_github(file_name):
    try:
        r = requests.get(f"{GITHUB_BASE}{file_name}", timeout=10)
        if r.status_code == 200:
            return [line.strip() for line in r.text.splitlines() if line.strip()]
    except: return []
    return []

def get_currency():
    """Отримує курси від ПриватБанку та Монобанку"""
    res_text = "💰 <b>Курси валют:</b>\n"
    
    # 1. ПриватБанк (Готівковий)
    try:
        privat = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd = next(x for x in privat if x['ccy'] == 'USD')
        eur = next(x for x in privat if x['ccy'] == 'EUR')
        res_text += f"🏦 <b>Приват:</b> 🇺🇸 {float(usd['buy']):.2f}/{float(usd['sale']):.2f} | 🇪🇺 {float(eur['buy']):.2f}/{float(eur['sale']):.2f}\n"
    except: res_text += "🏦 ПриватБанк: тимчасово недоступний\n"

    # 2. Монобанк та Крос-курс
    try:
        mono = requests.get("https://api.monobank.ua/bank/currency", timeout=5).json()
        # ISO коди: 840 - USD, 978 - EUR, 980 - UAH
        usd_m = next(x for x in mono if x['currencyCodeA'] == 840 and x['currencyCodeB'] == 980)
        eur_m = next(x for x in mono if x['currencyCodeA'] == 978 and x['currencyCodeB'] == 980)
        
        # Крос-курс (зазвичай це відношення курсів до гривні)
        cross_rate = eur_m['rateBuy'] / usd_m['rateBuy']
        
        res_text += f"🖤 <b>Моно:</b> 🇺🇸 {usd_m['rateBuy']:.2f}/{usd_m['rateSell']:.2f} | 🇪🇺 {eur_m['rateBuy']:.2f}/{eur_m['rateSell']:.2f}\n"
        res_text += f"📊 <b>Крос-курс EUR/USD:</b> {cross_rate:.3f}\n"
    except: res_text += "🖤 Монобанк: ліміт запитів або недоступний\n"
    
    return res_text

def send_morning_post():
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    now = datetime.now(kyiv_tz)
    date_key = now.strftime("%m-%d")
    
    # Дані з GitHub
    names_list = get_list_from_github("names.txt")
    names = next((l[6:] for l in names_list if l.startswith(date_key)), "дані відсутні")
    
    history_list = get_list_from_github("history.txt")
    history = next((l[6:] for l in history_list if l.startswith(date_key)), "подій не знайдено")
    
    # Лічильник Нового Року
    next_year = now.year + 1
    ny_date = datetime(next_year, 1, 1, tzinfo=kyiv_tz)
    days_left = (ny_date - now).days

    # Збірка тексту
    text = f"☀️ <b>Доброго ранку! Сьогодні {now.strftime('%d.%m.%Y')}</b>\n"
    text += "──────────────────\n"
    text += get_currency() + "\n"
    text += f"😇 <b>День ангела:</b> {names}\n\n"
    text += f"🕰 <b>Цей день в історії:</b>\n{history}\n\n"
    text += f"🎄 До Нового року залишилось: <b>{days_left}</b> днів"

    # Фото (1-26)
    img_num = random.randint(1, 26)
    img_url = f"{GITHUB_BASE}media/morning/{img_num}.png"
    
    try:
        img_data = requests.get(img_url).content
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                      files={"photo": ("image.png", img_data)}, 
                      data={"chat_id": CHAT_ID, "caption": text, "parse_mode": "HTML"})
    except:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

def send_quote_post():
    quotes = get_list_from_github("quotes.txt")
    if not quotes: return
    quote = random.choice(quotes)
    emoji = random.choice(["✨", "🌟", "💡", "🚀", "🎯", "🔥"])
    text = f"{emoji} <b>МОТИВАЦІЯ ДНЯ</b>\n\n«{quote}»\n\n🌈 <i>Зробіть цей день особливим!</i>"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    hour = datetime.now(kyiv_tz).hour
    
    # Логіка розподілу (за київським часом)
    if 5 <= hour <= 10:
        send_morning_post()
    else:
        send_quote_post()
