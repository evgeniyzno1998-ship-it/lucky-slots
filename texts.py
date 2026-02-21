# texts.py - Все тексты бота на польском

# Приветствие и старт
WELCOME = """
👋 Witaj w Kasyno PL Bot!

Oferujemy najlepsze oferty kasynowe w Polsce. Wybierz opcję z menu:

🎰 *Graj teraz* — lista kasyn z bonusami
🎁 *Bonusy* — aktualne promocje
👥 *Poleć znajomego* — zarabiaj Żetony Casino
💰 *Moje żetony* — sprawdź swój balans

Powodzenia! 🍀
"""

# Запрос номера с заманухой
PHONE_REQUEST = """
🎰 **Odbierz 50 darmowych spinów!**

📱 Zostaw swój numer telefonu, a my wyślemy Ci kod na 50 darmowych spinów po pierwszym depozycie!

👇 Kliknij przycisk poniżej, aby udostępnić numer:
"""

# После получения номера
PHONE_THANKS = """
✅ **Dziękujemy!** Numer został zapisany.

🎁 **50 darmowych spinów** czeka na Ciebie po pierwszym depozycie w dowolnym kasynie z naszej listy!

Wybierz kasyno i zacznij grać:
"""

# Меню выбора казино
CASINO_CHOOSE = "Wybierz kasyno:"

# Заголовок для бонусów
BONUS_HEADER = """
🎁 *Aktualne bonusy w kasynach:*

{slottica}
{magic365}
{gransino}
{slottyway}

Kliknij 🎰 *Graj teraz*, aby otrzymać link i odebrać bonus!
"""

# Информация о казино
CASINO_INFO = """
🎰 *{name}*

{bonus}

👉 [Kliknij tutaj, aby przejść do kasyna]({link})

Po rejestracji wpłać depozyt i odbierz bonus!
"""

# Реферальная система
REFERRAL_TEXT = """
👥 *Twój unikalny link polecający:*

`{link}`

📊 *Przyciągnąłeś już:* {count} znajomych
💰 *Twoje Żetony Casino:* {coins}

💡 *Jak to działa?*
- Za każdego znajomego, który wejdzie po Twoim linku i zapisze się do bota - otrzymujesz **10 Żetonów Casino**
- Wkrótce będziesz mógł wymienić żetony na ekskluzywne bonusy!
"""

# Баланс монет
COINS_BALANCE = """
💰 *Twój balans Żetonów Casino:*

**{coins} żetonów**

Zdobywaj żetony zapraszając znajomych!
1 znajomy = 10 żetonów
"""

# Админка
ADMIN_NO_USERS = "Brak użytkowników z numerami telefonów."
ADMIN_HEADER = "📱 *Użytkownicy z numerami:*\n\n"
ADMIN_LINE = "👤 {name} (@{username})\n🆔 {user_id}\n📞 {phone}\n📅 {date}\n💰 Żetony: {coins}\n👥 Zaprosił: {referrals}\n—\n"
ADMIN_TOP = "\n🏆 *TOP 10 REFERALÓW:*\n"
ADMIN_TOP_LINE = "{place}. {name} (@{username}) — {count} zaproszeń, {coins} żetonów\n"

ADMIN_DENIED = "⛔ Dostęp zabroniony"

LANGUAGES = {
    'pl': '🇵🇱 Polski',
    'ua': '🇺🇦 Українська',
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}

BOT_TEXTS = {
    'pl': {'play': '🎰 Graj teraz', 'settings': '⚙️ Język', 'buy': '💳 Kup żetony', 'welcome': 'Witaj в Lucky Slots!'},
    'ua': {'play': '🎰 Грати зараз', 'settings': '⚙️ Мова', 'buy': '💳 Купити жетони', 'welcome': 'Вітаємо у Lucky Slots!'},
    'ru': {'play': '🎰 Играть сейчас', 'settings': '⚙️ Язык', 'buy': '💳 Купить жетоны', 'welcome': 'Добро пожаловать в Lucky Slots!'},
    'en': {'play': '🎰 Play Now', 'settings': '⚙️ Language', 'buy': '💳 Buy Coins', 'welcome': 'Welcome to Lucky Slots!'}
}
