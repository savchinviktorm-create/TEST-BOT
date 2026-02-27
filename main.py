import os
import urllib.request
import json
from datetime import datetime

def get_history_event():
    # Отримуємо дату у форматі ММ-ДД (як у твоєму history.txt)
    today = datetime.now().strftime("%m-%d")
    url = "https://raw.githubusercontent.com/savchinviktorm-create/my-daily-bot/main/history.txt"
    
    try:
        # Стандартний спосіб завантажити файл без бібліотеки requests
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            for line in data.splitlines():
                if line.startswith(today):
                    # Повертаємо текст після дати і двокрапки
                    return line.split(':', 1)[1].strip()
        return "Сьогодні спокійний день, визначних подій не знайдено."
    except:
        return "Не вдалося завантажити історію дня."

def send_telegram():
    token = os.getenv('TOKEN') # Беремо токен з твоїх секретів (daily.yml рядок 27)
    chat_id = os.getenv('MY_CHAT_ID') # Беремо ID з секретів (daily.yml рядок 28)
    
    event = get_history_event()
    date_now = datetime.now().strftime("%d.%m.%Y")
    
    message_text = f"📅 **ЗВІТ НА {date_now}**\n\n📜 **Цей день в історії:**\n{event}"
    
    # Надсилаємо в Telegram через стандартний urllib
    send_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }).encode('utf-8')
    
    req = urllib.request.Request(send_url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode()
    except Exception as e:
        print(f"Помилка відправки: {e}")

if __name__ == "__main__":
    send_telegram()
