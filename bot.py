import logging, sqlite3, asyncio, time, os, sys, aiohttp
from collections import defaultdict
from typing import Callable, Any, Awaitable
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram import BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, TelegramObject, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ==================== НАСТРОЙКИ ====================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN")
API_PORT = int(os.getenv("PORT", 8081))
CRYPTOBOT_API = "https://pay.crypt.bot/api"

# ==================== ЛОКАЛИЗАЦИЯ ====================
LANGUAGES = {
    'pl': '🇵🇱 Polski',
    'ua': '🇺🇦 Українська',
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}

BOT_TEXTS = {
    'pl': {
        'welcome': 'Witaj в Lucky Slots! 🎰\nWybierz opcję poniżej:',
        'play': '🎰 Graj teraz',
        'buy': '💳 Kup żetony',
        'stats': '💰 Moje żetony',
        'ref': '👥 Poleć znajomego',
        'settings': '⚙️ Język / Мова',
        'balance': 'Twój balans: {coins} żetonów',
        'buy_menu': '💳 *Wybierz pakiet żetonów:*',
        'deposit_notif': 'Brak żetonów! Wybierz pakiet do doładowania 👇'
    },
    'ua': {
        'welcome': 'Вітаємо у Lucky Slots! 🎰\nОберіть дію:',
        'play': '🎰 Грати зараз',
        'buy': '💳 Купити жетони',
        'stats': '💰 Мій баланс',
        'ref': '👥 Запросити друга',
        'settings': '⚙️ Мова / Język',
        'balance': 'Ваш баланс: {coins} жетонів',
        'buy_menu': '💳 *Оберіть пакет жетонів:*',
        'deposit_notif': 'Немає жетонів! Оберіть пакет для поповнення 👇'
    },
    'ru': {
        'welcome': 'Добро пожаловать в Lucky Slots! 🎰\nВыберите действие:',
        'play': '🎰 Играть сейчас',
        'buy': '💳 Купить жетоны',
        'stats': '💰 Мой баланс',
        'ref': '👥 Рефералы',
        'settings': '⚙️ Язык / Język',
        'balance': 'Ваш баланс: {coins} жетонов',
        'buy_menu': '💳 *Выберите пакет жетонов:*',
        'deposit_notif': 'Нет жетонов! Выберите пакет для пополнения 👇'
    },
    'en': {
        'welcome': 'Welcome to Lucky Slots! 🎰\nChoose an option:',
        'play': '🎰 Play Now',
        'buy': '💳 Buy Coins',
        'stats': '💰 My Balance',
        'ref': '👥 Referrals',
        'settings': '⚙️ Language / Język',
        'balance': 'Your balance: {coins} coins',
        'buy_menu': '💳 *Choose a package:*',
        'deposit_notif': 'No coins! Choose a package to deposit 👇'
    }
}

# ==================== БАЗА ДАННЫХ ====================
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, 
                phone TEXT, referred_by INTEGER, referrals_count INTEGER DEFAULT 0, 
                coins INTEGER DEFAULT 0, joined_date TEXT, last_click TEXT, language TEXT DEFAULT 'pl'
            )
        ''')
        try: conn.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'pl'")
        except: pass
        conn.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY, user_id INTEGER, pack_key TEXT, 
                coins INTEGER, amount REAL, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT (datetime('now'))
            )
        ''')

def get_user_lang(user_id):
    with sqlite3.connect('users.db') as conn:
        res = conn.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return res[0] if res else 'pl'

def set_user_lang(user_id, lang):
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))

def get_user_stats(user_id):
    with sqlite3.connect('users.db') as conn:
        res = conn.execute("SELECT referrals_count, coins FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return res if res else (0, 0)

def add_coins(user_id, amount):
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))

def create_user(user_id, username, first_name, ref_id=None):
    with sqlite3.connect('users.db') as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date, referred_by) VALUES (?, ?, ?, datetime('now'), ?)",
                     (user_id, username, first_name, ref_id))

# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id):
    global BOT_USERNAME
    lang = get_user_lang(user_id)
    t = BOT_TEXTS[lang]
    # ПЕРЕДАЕМ API URL, ИМЯ БОТА И ЯЗЫК В ИГРУ
    webapp_url = f"https://evgeniyzno1998-ship-it.github.io/lucky-slots/?api=https://lucky-slots-production.up.railway.app&bot={BOT_USERNAME}&lang={lang}"
    
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t['play'], web_app=types.WebAppInfo(url=webapp_url))],
        [KeyboardButton(text=t['buy']), KeyboardButton(text=t['stats'])],
        [KeyboardButton(text=t['ref']), KeyboardButton(text=t['settings'])]
    ], resize_keyboard=True)

def packages_keyboard():
    COIN_PACKAGES = {"pack_50": ("50", 0.50), "pack_100": ("100", 0.90), "pack_500": ("500", 4.00)}
    builder = InlineKeyboardBuilder()
    for key, (label, price) in COIN_PACKAGES.items():
        builder.button(text=f"{label} żet. — {price} USDT", callback_data=f"buy_{key}")
    return builder.adjust(1).as_markup()

# ==================== БОТ И ДИСПАТЧЕР ====================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
BOT_USERNAME = ""

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    # Регистрация
    create_user(user_id, message.from_user.username, message.from_user.first_name)
    
    lang = get_user_lang(user_id)

    # Если переход из игры по кнопке "Депозит"
    if len(args) > 1 and args[1] == "deposit":
        await message.answer(BOT_TEXTS[lang]['deposit_notif'], reply_markup=packages_keyboard(), parse_mode="Markdown")
        return

    await message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(user_id))

# Хендлер настроек языка
@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['settings'] for l in BOT_TEXTS))
async def show_lang_menu(message: Message):
    builder = InlineKeyboardBuilder()
    for code, name in LANGUAGES.items():
        builder.button(text=name, callback_data=f"setlang_{code}")
    await message.answer("Choose language / Wybierz język:", reply_markup=builder.adjust(2).as_markup())

@dp.callback_query(F.data.startswith("setlang_"))
async def set_lang_callback(call: CallbackQuery):
    lang_code = call.data.split("_")[1]
    set_user_lang(call.from_user.id, lang_code)
    await call.message.answer(f"✅ Language: {LANGUAGES[lang_code]}", reply_markup=main_menu(call.from_user.id))
    await call.answer()

# Хендлер кнопки "Купить" (для всех языков)
@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['buy'] for l in BOT_TEXTS))
async def buy_handler(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(BOT_TEXTS[lang]['buy_menu'], reply_markup=packages_keyboard(), parse_mode="Markdown")

# Хендлер кнопки "Баланс" (для всех языков)
@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['stats'] for l in BOT_TEXTS))
async def balance_handler(message: Message):
    user_id = message.from_user.id
    _, coins = get_user_stats(user_id)
    lang = get_user_lang(user_id)
    await message.answer(BOT_TEXTS[lang]['balance'].format(coins=coins))

# ==================== API ДЛЯ MINI APP ====================
from aiohttp import web
import urllib.parse, hmac, hashlib, json

async def api_get_balance(request: web.Request) -> web.Response:
    init_data = request.rel_url.query.get("init_data", "")
    # (Упрощенная проверка для примера, в реальности используй verify_telegram_init_data)
    parsed = dict(urllib.parse.parse_qsl(init_data))
    user_data = json.loads(parsed.get("user", "{}"))
    user_id = user_data.get("id")
    _, coins = get_user_stats(user_id)
    return web.json_response({"ok": True, "balance": coins}, headers={"Access-Control-Allow-Origin": "*"})

async def api_spin(request: web.Request) -> web.Response:
    body = await request.json()
    parsed = dict(urllib.parse.parse_qsl(body.get("init_data", "")))
    user_id = json.loads(parsed.get("user", "{}")).get("id")
    bet, win = int(body.get("bet", 0)), int(body.get("winnings", 0))
    
    with sqlite3.connect('users.db') as conn:
        curr = conn.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
        if curr < bet: return web.json_response({"ok": False, "error": "No money"}, headers={"Access-Control-Allow-Origin": "*"})
        new_bal = curr - bet + win
        conn.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_bal, user_id))
        
    return web.json_response({"ok": True, "balance": new_bal}, headers={"Access-Control-Allow-Origin": "*"})

async def start_api_server():
    app = web.Application()
    app.router.add_get("/api/balance", api_get_balance)
    app.router.add_post("/api/spin", api_spin)
    app.router.add_options("/{tail:.*}", lambda r: web.Response(headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"}))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", API_PORT).start()

async def main():
    global BOT_USERNAME
    init_db()
    bot_info = await bot.get_me()
    BOT_USERNAME = bot_info.username
    asyncio.create_task(start_api_server())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
