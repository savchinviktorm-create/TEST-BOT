import os
import requests
from datetime import datetime
import pytz

def get_history_event():
    # Налаштовуємо часовий пояс Києва
    kyiv_tz = pytz.timezone('Europe/Kiev')
    today = datetime.now(kyiv_tz).strftime("%m-%d")
    
    # URL твого файлу (сира версія)
    # Заміни 'savchinviktorm-create/my-daily-bot' на свій актуальний шлях, якщо він інший
    url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/history.txt"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            lines = response.text.splitlines()
            for line in lines:
                # Шукаємо рядок, який починається з поточної дати (напр. 02-27)
                if line.startswith(today):
                    return line.split(':', 1)[1].strip()
        return "Сьогодні спокійний день, визначних подій не знайдено."
    except Exception as e:
        return f"Не вдалося завантажити історію: {e}"

def send_telegram_message():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    event = get_history_event()
    
    # Формуємо гарне повідомлення
    date_now = datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y")
    text = f"📅 **Звіт на {date_now}**\n\n📜 **Цей день в історії:**\n{event}"
    
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    requests.post(send_url, json=payload)

if __name__ == "__main__":
    send_telegram_message()
