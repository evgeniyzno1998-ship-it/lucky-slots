# Currency display rates (approximate, updated periodically)
CURRENCY_RATES = {
    'USD': 1.0,
    'EUR': 0.92,
    'PLN': 4.05,
    'UAH': 41.5,
    'RUB': 96.0,
    'GBP': 0.79,
}
CURRENCY_SYMBOLS = {'USD':'$','EUR':'€','PLN':'zł','UAH':'₴','RUB':'₽','GBP':'£'}

# Stars packages (Telegram Stars pricing)
STARS_PACKAGES = {"50": 50, "150": 150, "500": 500, "1000": 1000}
# USDT packages via CryptoBot
USDT_PACKAGES = {"1": 1.00, "5": 5.00, "10": 10.00, "25": 25.00, "50": 50.00}
# Legacy coins packages (kept for backward compat)
PACKAGES = {"50": 0.50, "100": 0.90, "500": 4.00}

# Localization
LANGUAGES = {'pl': '🇵🇱 Polski', 'ua': '🇺🇦 Українська', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
BOT_TEXTS = {
    'pl': {'welcome': 'Witaj w Lucky Slots! 🎰\nKliknij przycisk poniżej aby zagrać!', 'play': '🎰 Graj teraz', 'buy': '💳 Kup żetony', 'set': '⚙️ Język', 'bal': '💰 Moje żetony', 'ref': '👥 Poleć znajomego', 'balance_text': '💰 Twój balans: {c} żetonów', 'lang_ok': '✅ Język zmieniony!', 'token': 'żetonów', 'buy_m': '💳 Wybierz pakiet:', 'ref_t': '👥 <b>Twój link:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Zaprosiłeś: <b>{refs}</b>\n💰 Zdobyłeś: <b>{earned}</b> żetonów\n\n💡 Za każdego: <b>{bonus}</b> żetonów!', 'ref_welcome': '🎉 Bonus {bonus} żetonów!', 'ref_earned': '🎉 +{bonus} żetonów za polecenie!', 'pay_success': '✅ +{amount} żetonów!\nBalans: {balance}', 'pay_pending': '⏳ Kliknij aby zapłacić:'},
    'ua': {'welcome': 'Вітаємо у Lucky Slots! 🎰\nНатисніть кнопку щоб грати!', 'play': '🎰 Грати', 'buy': '💳 Купити жетони', 'set': '⚙️ Мова', 'bal': '💰 Баланс', 'ref': '👥 Друзі', 'balance_text': '💰 Баланс: {c} жетонів', 'lang_ok': '✅ Мову змінено!', 'token': 'жетонів', 'buy_m': '💳 Оберіть пакет:', 'ref_t': '👥 <b>Посилання:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Запросили: <b>{refs}</b>\n💰 Зароблено: <b>{earned}</b>\n\n💡 За кожного: <b>{bonus}</b>!', 'ref_welcome': '🎉 Бонус {bonus} жетонів!', 'ref_earned': '🎉 +{bonus} жетонів!', 'pay_success': '✅ +{amount} жетонів!\nБаланс: {balance}', 'pay_pending': '⏳ Натисніть для оплати:'},
    'ru': {'welcome': 'Добро пожаловать! 🎰\nНажмите кнопку чтобы играть!', 'play': '🎰 Играть', 'buy': '💳 Купить жетоны', 'set': '⚙️ Язык', 'bal': '💰 Баланс', 'ref': '👥 Друзья', 'balance_text': '💰 Баланс: {c} жетонов', 'lang_ok': '✅ Язык изменен!', 'token': 'жетонов', 'buy_m': '💳 Выберите пакет:', 'ref_t': '👥 <b>Ссылка:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Приглашено: <b>{refs}</b>\n💰 Заработано: <b>{earned}</b>\n\n💡 За каждого: <b>{bonus}</b>!', 'ref_welcome': '🎉 Бонус {bonus} жетонов!', 'ref_earned': '🎉 +{bonus} жетонов!', 'pay_success': '✅ +{amount} жетонов!\nБаланс: {balance}', 'pay_pending': '⏳ Нажмите для оплаты:'},
    'en': {'welcome': 'Welcome to Lucky Slots! 🎰\nTap the button to play!', 'play': '🎰 Play', 'buy': '💳 Buy Coins', 'set': '⚙️ Language', 'bal': '💰 Balance', 'ref': '👥 Friends', 'balance_text': '💰 Balance: {c} coins', 'lang_ok': '✅ Language changed!', 'token': 'coins', 'buy_m': '💳 Choose package:', 'ref_t': '👥 <b>Link:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Invited: <b>{refs}</b>\n💰 Earned: <b>{earned}</b>\n\n💡 Per friend: <b>{bonus}</b>!', 'ref_welcome': '🎉 Bonus {bonus} coins!', 'ref_earned': '🎉 +{bonus} coins!', 'pay_success': '✅ +{amount} coins!\nBalance: {balance}', 'pay_pending': '⏳ Click to pay:'},
}

# Symbols & weights
BASE_SYMS = ['🍒', '🍋', '🍊', '🍇', '🍫', '🍭', '🍬', '💎']
BONUS_SYMS = ['👑', '💎', '⭐', '❤️', '🍀', '🧲', '💰', '🌈']
SCATTER = '🎰'
BOMB = '💣'
BOMB_WEIGHTS = [(50,2),(25,3),(12,5),(6,8),(3,10),(2,15),(1,25),(0.5,50),(0.2,100)]

WHEEL_PRIZES = [
    (30,'coins',5),(25,'coins',10),(15,'coins',25),(10,'coins',50),
    (8,'coins',100),(5,'free_spins',3),(4,'free_spins',5),(2,'coins',250),(1,'coins',500),
]

VIP_LEVELS = [
    {'name':'Bronze','icon':'🥉','min':0,'cb':1},
    {'name':'Silver','icon':'🥈','min':1000,'cb':2},
    {'name':'Gold','icon':'🥇','min':5000,'cb':3},
    {'name':'Platinum','icon':'💎','min':25000,'cb':5},
    {'name':'Diamond','icon':'👑','min':100000,'cb':8},
]

# API Headers
H = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With"
}
