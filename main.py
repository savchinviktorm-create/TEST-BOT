import requests
import random
import datetime
import os
import pytz

# --- НАЛАШТУВАННЯ ---
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "583e99233cb332aaf8ab0ded7a92dde7")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8779933996:AAFtTmrPZ3qME5WV3ZRf7rfOHKzxbCsmSFY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "653398188")
KIEV_TZ = pytz.timezone('Europe/Kiev')

def get_now():
    return datetime.datetime.now(KIEV_TZ)

def send_telegram(text, photo_path=None):
    if photo_path and os.path.exists(photo_path):
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": text, "parse_mode": "HTML"}
            files = {"photo": photo}
            r = requests.post(url, data=payload, files=files)
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        r = requests.post(url, json=payload)
    return r.json()

def get_currency_logic():
    res = "💰 <b>КУРС ВАЛЮТ (Середній)</b>\n"
    try:
        p = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11", timeout=10).json()
        usd_p = next(i for i in p if i['ccy'] == 'USD')
        eur_p = next(i for i in p if i['ccy'] == 'EUR')
        m = requests.get("https://api.monobank.ua/bank/currency", timeout=10).json()
        usd_m = next(i for i in m if i['currencyCodeA'] == 840 and i['currencyCodeB'] == 980)
        eur_m = next(i for i in m if i['currencyCodeA'] == 978 and i['currencyCodeB'] == 980)
        avg_usd_buy = (float(usd_p['buy']) + float(usd_m['rateBuy'])) / 2
        avg_usd_sale = (float(usd_p['sale']) + float(usd_m['rateSell'])) / 2
        avg_eur_buy = (float(eur_p['buy']) + float(eur_m['rateBuy'])) / 2
        avg_eur_sale = (float(eur_p['sale']) + float(eur_m['rateSell'])) / 2
        cross_rate = avg_usd_sale / avg_eur_sale
        res += f"🇺🇸 USD: {avg_usd_buy:.2f}/{avg_usd_sale:.2f}\n"
        res += f"🇪🇺 EUR: {avg_eur_buy:.2f}/{avg_eur_sale:.2f}\n"
        res += f"⚖️ Крос-курс (USD/EUR): {cross_rate:.3f}\n"
        res += f"🏦 Приват: {usd_p['sale'][:5]} / 🐱 Моно: {usd_m['rateSell']}"
    except:
        res += "⚠️ Курс тимчасово недоступний"
    return res

def get_random_image(folder):
    if not os.path.exists(folder): return None
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(folder, random.choice(files)) if files else None

def get_data_by_date(filename):
    try:
        today_str = get_now().strftime("%m-%d")
        if not os.path.exists(filename): return "Дані оновлюються"
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(today_str):
                    return line[6:].strip()
        return "Дані оновлюються"
    except: return "Помилка файлу"

def get_random_lines(filename, count=1):
    try:
        if not os.path.exists(filename): return ["Дані відсутні"]
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return random.sample(lines, min(len(lines), count)) if lines else ["Дані відсутні"]
    except: return ["Помилка"]

def days_to_ny():
    today = get_now().date()
    ny = datetime.date(today.year + 1, 1, 1)
    return (ny - today).days

def get_movie():
    try:
        page = random.randint(1, 10)
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=uk-UA&page={page}"
        r = requests.get(url, timeout=10).json()
        m = random.choice(r['results'])
        return f"🎬 <b>ВЕЧІРНІЙ КІНОЗАЛ</b>\n🎥 <b>{m.get('title')}</b>\n⭐ Рейтинг: {m.get('vote_average')}\n🍿 {m.get('overview')[:200]}..."
    except: return "🎬 Час для кіно!"

def make_post():
    now = get_now()
    hour = now.hour

    # 30 варіантів для порад
    advice_intros = [
        "💡 <b>Корисна порада для вас:</b>", "🛠 <b>Спробуйте цей лайфхак:</b>", "🧠 <b>Маленька хитрість на сьогодні:</b>",
        "✨ <b>Пропозиція дня:</b>", "📝 <b>Варто спробувати:</b>", "🎯 <b>Порада для продуктивності:</b>",
        "⚙️ <b>Лайфхак, що спрощує життя:</b>", "💡 <b>А ви знали про такий метод?</b>", "🛡 <b>Корисна знахідка:</b>",
        "📎 <b>Занотуйте собі це:</b>", "🧘 <b>Для вашого комфорту:</b>", "⚡️ <b>Швидка порада:</b>",
        "🏠 <b>Побутова хитрість:</b>", "💎 <b>Цінна порада:</b>", "🌈 <b>Для гарного настрою:</b>",
        "🔋 <b>Енергійна порада:</b>", "📂 <b>З копілки мудрості:</b>", "🔑 <b>Ключ до успіху:</b>",
        "🔍 <b>Цікаве рішення:</b>", "📐 <b>Практичний підхід:</b>", "💊 <b>Рецепт гарного дня:</b>",
        "🧨 <b>Вибухова ідея:</b>", "🧨 <b>Простий секрет:</b>", "🍎 <b>Для вашого здоров'я:</b>",
        "📈 <b>Порада для росту:</b>", "🤝 <b>Дружня рекомендація:</b>", "🎁 <b>Маленький бонус для вас:</b>",
        "🛸 <b>Космічний лайфхак:</b>", "🧿 <b>На замітку:</b>", "🪄 <b>Магія буденності:</b>"
    ]

    # 30 варіантів для фактів
    fact_intros = [
        "🧐 <b>А чи знали ви, що...</b>", "🌍 <b>Цікавий факт у світі:</b>", "🔍 <b>Цікаво знати:</b>",
        "📖 <b>Виявляється, що:</b>", "🧬 <b>Наука каже наступне:</b>", "🗿 <b>Історичний факт:</b>",
        "🪐 <b>Таємниця всесвіту:</b>", "📸 <b>Погляд на світ:</b>", "💬 <b>Чи чули ви про таке?</b>",
        "🕵️‍♂️ <b>Ми знайшли дещо цікаве:</b>", "💡 <b>Факт, що вражає:</b>", "🌊 <b>Глибокі знання:</b>",
        "🔭 <b>У фокусі уваги:</b>", "📜 <b>Архівна знахідка:</b>", "🧸 <b>Милий факт:</b>",
        "🦖 <b>Давним-давно:</b>", "🤖 <b>Техно-факт:</b>", "🧩 <b>Частина загадки:</b>",
        "🦜 <b>Диво природи:</b>", "🏜 <b>Неймовірна реальність:</b>", "🏟 <b>Культурна цікавинка:</b>",
        "🛤 <b>Шлях пізнання:</b>", "🗻 <b>Вершина знань:</b>", "🕯 <b>Проливаємо світло:</b>",
        "⏳ <b>Минуле і теперішнє:</b>", "🏹 <b>Точно в ціль:</b>", "🛶 <b>Потік інформації:</b>",
        "🛰 <b>З висоти пташиного польоту:</b>", "🕯 <b>Секретний факт:</b>", "🧿 <b>Дивовижне поруч:</b>"
    ]

    # 30 варіантів для іменин
    name_day_intros = [
        "🎂 <b>Сьогодні іменини святкують:</b>", "🎉 <b>День ангела сьогодні у:</b>", "🌟 <b>Сьогодні день ангела відзначають:</b>",
        "🎈 <b>Сьогодні іменинники:</b>", "🎁 <b>Своє свято святкують:</b>", "🥂 <b>Вітаємо з днем ангела:</b>",
        "🕯 <b>Сьогодні особливий день у:</b>", "✨ <b>Небесного опікуна вшановують:</b>", "🕊 <b>Сьогодні вітаємо:</b>",
        "💐 <b>Квіти та вітання сьогодні для:</b>", "🎀 <b>День ангела прийшов до:</b>", "🧁 <b>Солодкі вітання іменинникам:</b>",
        "🔔 <b>Сьогодні іменинний дзвін для:</b>", "🧸 <b>Зі святом вітаємо:</b>", "💌 <b>Надсилаємо промені добра для:</b>",
        "💎 <b>Особлива дата у:</b>", "🎊 <b>Зустрічайте іменинників:</b>", "🧸 <b>День вашого імені:</b>",
        "🪞 <b>Сьогодні іменини у:</b>", "🪁 <b>Вітання летять до:</b>", "🍯 <b>Медові привітання для:</b>",
        "🧿 <b>Ваш ангел сьогодні поруч:</b>", "🕯 <b>Вітаємо власників імен:</b>", "⛲️ <b>Сьогодні свято у:</b>",
        "🎠 <b>Радісний день у:</b>", "⛲️ <b>Ваше ім'я сьогодні звучить частіше у:</b>", "🔮 <b>Ангел-охоронець святкує з:</b>",
        "🧨 <b>Бажаємо щастя сьогодні:</b>", "🥁 <b>Сьогоднішні винуватці свята:</b>", "🧿 <b>Запишіть, у кого сьогодні іменини:</b>"
    ]

    # 30 варіантів заклику привітати
    congratulation_texts = [
        "Не забудьте привітати знайомих, якщо вони серед вашого кола друзів! 🥂",
        "Чудова нагода зателефонувати друзям та привітати їх! 🎈",
        "Якщо маєте знайомих з цими іменами — обов'язково надішліть їм вітання! 🎁",
        "Маленьке повідомлення імениннику зробить його день кращим! 💌",
        "Поділіться радістю з друзями, які сьогодні святкують! ✨",
        "Привітання — це дрібниця, яка дуже зігріває серце. Напишіть їм! 😊",
        "Сьогодні гарний день, щоб згадати про знайомих іменинників! ☀️",
        "Встигніть побажати всього найкращого винуватцям свята! 🎂",
        "Ангели люблять, коли їхніх підопічних вітають! 👼",
        "Ваше привітання сьогодні буде дуже доречним! 🧸",
        "Не тримайте добро в собі — привітайте друзів! 🕊",
        "Зробіть приємний сюрприз сьогоднішнім іменинникам! 🎀",
        "Ваш дзвінок може стати найкращим подарунком! 📱",
        "Сьогодні імена звучать як пісня. Приєднайтеся до вітань! 🎶",
        "Згадайте, хто з ваших близьких сьогодні святкує! 👀",
        "Маєте друзів з цими іменами? Напишіть їм пару теплих слів! 🔥",
        "Даруйте усмішки та привітання сьогодні! 💐",
        "Щирі слова завжди доречні. Вітаємо разом! 🌟",
        "Нехай ваші друзі відчують вашу увагу сьогодні! 💎",
        "Сьогодні день сповнений світла для цих імен. Поділіться ним! 🕯",
        "Гарна нагода відновити спілкування через привітання! 🤝",
        "Не забудьте надіслати листівку або тепле слово! 📮",
        "Свято стає кращим, коли про нього пам'ятають друзі! 🎊",
        "Сьогоднішні іменинники чекають на вашу увагу! 🍭",
        "Складіть коротке вітання для близьких! ✍️",
        "Хай ваш привітальний пост або смс зігріє когось! 🧣",
        "Ви знаєте, що робити — теплі слова самі себе не напишуть! 😉",
        "Сьогодні іменинники заслуговують на ваші обійми (хоча б віртуальні)! 🤗",
        "Будьте першим, хто привітає сьогоднішніх героїв дня! 🥇",
        "Світ стає добрішим від щирих привітань! 🌎"
    ]

    # 30 варіантів для жартів
    joke_intros = [
        "😂 <b>Час для усмішки:</b>", "🤪 <b>Трохи гумору вам у стрічку:</b>", "🔔 <b>А ось і свіжий анекдот:</b>",
        "🎭 <b>Хвилинка позитиву:</b>", "🍭 <b>Для солодкого настрою:</b>", "🤡 <b>Трохи жартів не завадить:</b>",
        "🧩 <b>Гумор — це життя:</b>", "🧸 <b>Посміхніться, вам це личить:</b>", "🥁 <b>Заряджаємо позитивом:</b>",
        "🧨 <b>Вибухова порція сміху:</b>", "🧿 <b>Налаштовуємося на радість:</b>", "🎡 <b>Карусель гумору:</b>",
        "🎷 <b>Весела нота дня:</b>", "🎨 <b>Розфарбуйте день сміхом:</b>", "🧘 <b>Йога для обличчя (сміх):</b>",
        "🌋 <b>Вулкан веселощів:</b>", "🚀 <b>Космічна порція жартів:</b>", "🧿 <b>Усмішка — найкраща зброя:</b>",
        "🚲 <b>Легкий гумор:</b>", "🚤 <b>Хвиля сміху:</b>", "⛲️ <b>Джерело позитиву:</b>",
        "🏔 <b>Вершина дотепності:</b>", "🗿 <b>Класика жанру:</b>", "🎲 <b>Граємо в настрій:</b>",
        "🏹 <b>Жарт у самісіньке серце:</b>", "🧩 <b>Знайдіть час пореготати:</b>", "🪁 <b>Легкість у кожному жарті:</b>",
        "🧿 <b>Магія гумору:</b>", "🕯 <b>Світла хвилинка:</b>", "🧨 <b>Бум сміху!</b>"
    ]

    if 5 <= hour < 11:
        img = get_random_image("media/morning")
        advice = get_random_lines('advices.txt', 1)[0]
        names = get_data_by_date('history.txt')
        
        text = (f"🌅 <b>ДОБРОГО РАНКУ!</b>\n📅 Сьогодні: {now.strftime('%d.%m.%Y')}\n"
                f"━━━━━━━━━━━━━━\n"
                f"{random.choice(name_day_intros)}\n└ 👤 {names}\n"
                f"<i>{random.choice(congratulation_texts)}</i>\n\n"
                f"🎉 <b>Свята:</b> {get_data_by_date('Holiday.txt')}\n"
                f"📜 <b>Цей день в історії:</b> {get_data_by_date('Wiking.txt')}\n"
                f"━━━━━━━━━━━━━━\n"
                f"{get_currency_logic()}\n"
                f"🎄 До Нового Року: {days_to_ny()} дн.\n"
                f"━━━━━━━━━━━━━━\n"
                f"{random.choice(advice_intros)}\n└ 💡 {advice}")
        return text, img

    elif hour >= 20 or hour < 5:
        img = get_random_image("media/evening")
        advices = get_random_lines('advices.txt', 2)
        facts = get_random_lines('facts.txt', 2)
        jokes = get_random_lines('jokes.txt', 2)
        
        text = (f"{random.choice(advice_intros)}\n└ 📍 {advices[0]}\n└ 📍 {advices[1]}\n\n"
                f"{random.choice(fact_intros)}\n└ 🔍 {facts[0]}\n└ 🔍 {facts[1]}\n\n"
                f"{random.choice(joke_intros)}\n└ ✨ {jokes[0]}\n└ ✨ {jokes[1]}\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"{get_movie()}")
        return text, img

    else:
        img = get_random_image("media/evening")
        advices = get_random_lines('advices.txt', 2)
        facts = get_random_lines('facts.txt', 2)
        
        text = (f"{random.choice(advice_intros)}\n└ 📍 {advices[0]}\n└ 📍 {advices[1]}\n\n"
                f"{random.choice(fact_intros)}\n└ 🔍 {facts[0]}\n└ 🔍 {facts[1]}")
        return text, img

if __name__ == "__main__":
    content, photo = make_post()
    response = send_telegram(content, photo)
    print(f"Результат відправки: {response}")
