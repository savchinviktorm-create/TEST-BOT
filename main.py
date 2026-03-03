import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TELEGRAM_TOKEN = "8697253866:AAHx3nS_Bshn5bamwbdTQZCtOZ6pfT8tmjY"
TELEGRAM_CHAT_ID = "653398188"
KIEV_TZ = pytz.timezone('Europe/Kiev')

WISHES = [
    "Нехай кожна сторінка дарує натхнення!", "Смачної кави та захопливого сюжету!", 
    "Ідеальний вечір — це ви і нова книга.", "Відкрийте для себе новий світ сьогодні!",
    "Нехай книга стане вашою найкращою подорожжю.", "Затишку вашому дому та серцю."
]

def get_books():
    # Список ключових слів для пошуку реального контенту
    keywords = ["художня література", "сучасна проза", "трилер", "історія України", "фентезі"]
    kw = random.choice(keywords)
    
    # Прямий запит без жорстких фільтрів по мові (фільтруємо вручну)
    url = f"https://www.googleapis.com/books/v1/volumes?q={kw}&langRestrict=uk&orderBy=relevance&maxResults=20"
    
    try:
        r = requests.get(url, timeout=15)
        items = r.json().get('items', [])
        
        if not items:
            return "📘 <b>ВИБІР РЕДАКЦІЇ</b>\n✍️ <i>Сучасна література</i>\n〰️〰️〰️〰️〰️〰️〰️〰️\n«Книги вже в дорозі до нашої віртуальної бібліотеки. Зачекайте наступного випуску!»\n\n"

        random.shuffle(items)
        res = ""
        count = 0
        for item in items:
            if count >= 3: break
            info = item.get('volumeInfo', {})
            
            title = info.get('title', 'Без назви').upper()
            author = ", ".join(info.get('authors', ['Автор невідомий']))
            desc = info.get('description', '')

            # Якщо немає опису — беремо категорію або коротку замітку
            if not desc:
                categories = info.get('categories', ['Література'])
                desc = f"Чудова книга у жанрі {categories[0]}. Рекомендуємо до прочитання!"

            # Обрізання
            limit = 350
            if len(desc) > limit:
                trunc = desc[:limit]
                last = max(trunc.rfind('.'), trunc.rfind('!'), trunc.rfind('?'))
                desc = trunc[:last+1] if last != -1 else trunc + "..."
            
            res += f"📘 <b>{title}</b>\n✍️ <i>{author}</i>\n"
            res += f"〰️〰️〰️〰️〰️〰️〰️〰️\n"
            res += f"«{desc}»\n\n"
            count += 1
        return res
    except:
        return "⚠️ Тимчасовий збій у бібліотеці."

def main():
    now = datetime.datetime.now(KIEV_TZ)
    date_str = now.strftime('%d.%m.%Y')
    
    header = f"✧─── ･ ｡ﾟ☆: *. 📖 .* :☆ﾟ. ───✧\n"
    header += f"🗓 <b>КНИЖКОВА СЕРЕДА • {date_str}</b>\n"
    header += f"✧─── ･ ｡ﾟ☆: *. 📚 .* :☆ﾟ. ───✧\n\n"
    
    body = get_books()
    footer = f"✨ <b>{random.choice(WISHES)}</b>"
    
    full_text = header + body + footer
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": full_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    main()
