def get_trending_books():
    try:
        # Змінюємо запит на більш загальний, щоб точно були результати
        # Шукаємо за ключовим словом "Україна" або "сучасна література" українською мовою
        url = "https://www.googleapis.com/books/v1/volumes?q=subject:fiction+l:uk&orderBy=relevance&maxResults=15"
        
        r = requests.get(url, timeout=15)
        print(f"Статус запиту: {r.status_code}") # Побачиш у логах GitHub
        
        data = r.json()
        items = data.get('items', [])
        
        if not items:
            # Резервний запит, якщо перший не спрацював
            url_backup = "https://www.googleapis.com/books/v1/volumes?q=intitle:книга+l:uk&maxResults=10"
            items = requests.get(url_backup).json().get('items', [])

        if not items:
            return "📖 На жаль, книжкова полиця порожня. Спробуємо пізніше!\n\n"

        random.shuffle(items)
        res = "📖 <b>ТОП-3 КНИЖКОВИХ ТРЕНДІВ:</b>\n\n"
        count = 0
        
        for item in items:
            if count >= 3: break
            info = item.get('volumeInfo', {})
            
            # Перевіряємо наявність опису, щоб не було порожньо
            desc = info.get('description', '')
            if not desc or len(desc) < 20: continue 

            title = info.get('title', 'Без назви')
            authors = ", ".join(info.get('authors', ['Автор невідомий']))

            # Розумне обрізання
            limit = 350
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
        return f"⚠️ Помилка отримання книг: {str(e)}\n\n"
