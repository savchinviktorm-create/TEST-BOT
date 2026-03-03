import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ (ВСТАВ СВОЇ ДАНІ СЮДИ) ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
TELEGRAM_TOKEN = "8697253866:AAHx3nS_Bshn5bamwbdTQZCtOZ6pfT8tmjY"  # Встав сюди токен @Slid48bot
TELEGRAM_CHAT_ID = "653398188"               # Твій ID вже вписано
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    # Обрізаємо текст під ліміт Telegram для фото (1024 символи)
    final_text = text[:1020] + "..." if len(text) > 1024 else text
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/send{'Photo' if photo_path else 'Message'}"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "caption" if photo_path else "text": final_text, 
        "parse_mode": "HTML"
    }
    
    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            return requests.post(url, data=payload, files={"photo": photo}).json()
    return requests.post(url, json=payload).json()

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ</b>\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=5).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        res += f"🏦 <b>Приват:</b> USD: {usd_p['buy'][:5]}/{usd_p['sale'][:5]} | EUR: {eur_p['buy'][:5]}/{eur_p['sale'][:5]}\n"
    except: res += "⚠️ Курс недоступний\n"
    return res

def get_random_lines(filename):
    path = filename if os.path.exists(filename) else f"{filename}.txt"
    if not os.path.exists(path): return "Цікавий факт вже готується..."
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.choice(lines) if lines else "Сьогодні без фактів."
    except: return "Дані оновлюються..."

def get_random_image(folder):
    if not os.path.exists(folder): return None
    try:
        files = [f for f in os
