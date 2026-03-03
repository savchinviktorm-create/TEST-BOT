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

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    r = requests.post(url, json=payload)
    res = r.json()
    if not res.get("ok"):
        print(f"❌ Помилка Telegram: {res.get('description')}")
    else:
        print("✅ Повідомлення успішно відправлено!")
    return res

def get_trending_books():
    try:
        # Прямий запит на популярні книги
        url = "https://www.googleapis.com/books/v1/volumes?q=intitle:книга+l:uk&orderBy=relevance&maxResults=15"
        r = requests.get(url, timeout=15)
        items = r.json().get('items', [])
        
        if not items:
            return "📖 На жаль, книг не знайдено."

        random.shuffle(items)
        res = "📖 <b>ТОП-3 КНИЖКОВИХ ТРЕНДІВ:</b>\n\n"
        count = 0
        for item in items:
            if count >= 3: break
            info = item.get('volumeInfo', {})
            desc = info.get('description', '')
            if not desc or len(desc) < 30: continue 

            title = info.get('title', 'Без назви')
            authors = ", ".join(info.get('authors', ['Автор невідомий']))

            limit = 400
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
        return f"⚠️ Помилка API: {str(e)}"

if __name__ == "__main__":
    print("🚀 Запуск тестового поста...")
    now = datetime.datetime.now(KIEV_TZ)
    
    # ПРИМУСОВИЙ ТЕКСТ БЕЗ ПЕРЕВІРКИ ДНЯ
    test_text = (f"🗓 <b>ТЕСТОВИЙ ВИПУСК • {now.strftime('%d.%m.%Y')}</b>\n"
                 f"----------------------------------\n\n"
                 f"{get_trending_books()}"
                 f"🔖 <i>Перевірка зв'язку!</i>")
    
    send_telegram(test_text)
