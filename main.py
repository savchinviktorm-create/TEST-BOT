import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = "583e99233cb332aaf8ab0ded7a92dde7"
TELEGRAM_TOKEN = "8697253866:AAHx3nS_Bshn5bamwbdTQZCtOZ6pfT8tmjY"
TELEGRAM_CHAT_ID = "653398188"
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload)
    return r.json()

def get_trending_books():
    try:
        url = "https://www.googleapis.com/books/v1/volumes?q=language:uk&orderBy=newest&maxResults=10"
        r = requests.get(url, timeout=10)
        data = r.json()
        items = data.get('items', [])
        random.shuffle(items)
        
        res = "📖 <b>ТОП-3 КНИЖКОВИХ ТРЕНДІВ:</b>\n\n"
        count = 0
        for item in items:
            if count >= 3: break
            info = item.get('volumeInfo', {})
            title = info.get('title', 'Без назви')
            authors = ", ".join(info.get('authors', ['Автор невідомий']))
            desc = info.get('description', 'Опис відсутній...')

            # Розумне обрізання
            limit = 300
            if len(desc) > limit:
                truncated = desc[:limit]
                last_dot = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
                desc = truncated[:last_dot + 1] if last_dot != -1 else truncated + "..."
            
            res += f"📚 <b>{title.upper()}</b>\n"
            res += f"✍️ <i>{authors}</i>\n"
            res += f"📝 {desc}\n\n"
            count += 1
        return res
    except Exception as e:
        return f"Помилка API: {str(e)}"

def make_test_post():
    now = get_now()
    date_str = now.strftime('%d.%m.%Y')
    
    body = get_trending_books()
    
    full_text = (f"🗓 <b>КНИЖКОВА СЕРЕДА • {date_str}</b>\n"
                 f"----------------------------------\n\n"
                 f"{body}"
                 f"🔖 <i>Приємного читання та натхнення!</i>")
    return full_text

if __name__ == "__main__":
    text_to_send = make_test_post()
    result = send_telegram(text_to_send)
    print(result)
