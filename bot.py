import logging, sqlite3, asyncio, time, os, sys, aiohttp, json, urllib.parse
from collections import defaultdict
from typing import Callable, Any, Awaitable
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, TelegramObject, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# ==================== НАСТРОЙКИ ====================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN")
API_PORT = int(os.getenv("PORT", 8081))
CRYPTOBOT_API = "https://pay.crypt.bot/api"

if not BOT_TOKEN or not ADMIN_ID or not CRYPTO_TOKEN:
    sys.exit("ERROR: Проверьте переменные окружения!")

# ==================== ЛОКАЛИЗАЦИЯ ====================
LANGUAGES = {'pl': '🇵🇱 Polski', 'ua': '🇺🇦 Українська', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}

BOT_TEXTS = {
    'pl': {
        'welcome': 'Witaj w Lucky Slots! 🎰\nWybierz opcję poniżej:',
        'play': '🎰 Graj teraz', 'buy': '💳 Kup żetony', 'stats': '💰 Moje żetony', 'ref': '👥 Poleć znajomego', 'settings': '⚙️ Język',
        'balance_text': 'Twój balans: {c} żetonów', 'dep_notif': 'Brak żetonów! Wybierz пакет 👇', 'lang_ok': '✅ Język zmieniony!', 
        'token': 'żetonów', 'ref_text': '🔗 Twój link: https://t.me/{b}?start=ref{u}\n👥 Poleceni: {cnt}', 'buy_menu': '💳 *Wybierz pakiet:*'
    },
    'ua': {
        'welcome': 'Вітаємо у Lucky Slots! 🎰\nОберіть дію:',
        'play': '🎰 Грати зараз', 'buy': '💳 Купити жетони', 'stats': '💰 Мій баланс', 'ref': '👥 Запросити друга', 'settings': '⚙️ Мова',
        'balance_text': 'Ваш баланс: {c} жетонів', 'dep_notif': 'Немає жетонів! Оберіть пакет 👇', 'lang_ok': '✅ Мову змінено!', 
        'token': 'жетонів', 'ref_text': '🔗 Посилання: https://t.me/{b}?start=ref{u}\n👥 Запрошено: {cnt}', 'buy_menu': '💳 *Оберіть пакет:*'
    },
    'ru': {
        'welcome': 'Добро пожаловать в Lucky Slots! 🎰\nВыберите действие:',
        'play': '🎰 Играть сейчас', 'buy': '💳 Купить жетоны', 'stats': '💰 Мой баланс', 'ref': '👥 Рефералы', 'settings': '⚙️ Язык',
        'balance_text': 'Ваш баланс: {c} жетонов', 'dep_notif': 'Нет жетонов! Выберите пакет 👇', 'lang_ok': '✅ Язык изменен!', 
        'token': 'жетонов', 'ref_text': '🔗 Ссылка: https://t.me/{b}?start=ref{u}\n👥 Рефералов: {cnt}', 'buy_menu': '💳 *Выберите пакет:*'
    },
    'en': {
        'welcome': 'Welcome to Lucky Slots! 🎰\nChoose an option:',
        'play': '🎰 Play Now', 'buy': '💳 Buy Coins', 'stats': '💰 My Balance', 'ref': '👥 Referrals', 'settings': '⚙️ Language',
        'balance_text': 'Your balance: {c} coins', 'dep_notif': 'No coins! Choose a package 👇', 'lang_ok': '✅ Language changed!', 
        'token': 'coins', 'ref_text': '🔗 Your link: https://t.me/{b}?start=ref{u}\n👥 Referrals: {cnt}', 'buy_menu': '💳 *Choose a package:*'
    }
}

# ==================== БАЗА ДАННЫХ ====================
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, phone TEXT,
            referred_by INTEGER, referrals_count INTEGER DEFAULT 0, coins INTEGER DEFAULT 0,
            joined_date TEXT, language TEXT DEFAULT 'pl')''')
        try: conn.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'pl'")
        except: pass
        conn.execute('''CREATE TABLE IF NOT EXISTS invoices (
            invoice_id TEXT PRIMARY KEY, user_id INTEGER, pack_key TEXT, coins INTEGER,
            amount REAL, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT (datetime('now')))''')

def get_user_lang(user_id):
    with sqlite3.connect('users.db') as conn:
        res = conn.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return res[0] if res else 'pl'

def get_user_stats(user_id):
    with sqlite3.connect('users.db') as conn:
        return conn.execute("SELECT referrals_count, coins FROM users WHERE user_id = ?", (user_id,)).fetchone() or (0, 0)

# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id, bot_name):
    lang = get_user_lang(user_id)
    t = BOT_TEXTS[lang]
    api_url = f"https://lucky-slots-production.up.railway.app"
    webapp_url = f"https://evgeniyzno1998-ship-it.github.io/lucky-slots/?api={api_url}&bot={bot_name}&lang={lang}"
    
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t['play'], web_app=WebAppInfo(url=webapp_url))],
        [KeyboardButton(text=t['buy']), KeyboardButton(text=t['stats'])],
        [KeyboardButton(text=t['ref']), KeyboardButton(text=t['settings'])]
    ], resize_keyboard=True)

def packages_keyboard(lang):
    t_name = BOT_TEXTS[lang]['token']
    builder = InlineKeyboardBuilder()
    pkgs = {"pack_50": (50, 0.50), "pack_100": (100, 0.90), "pack_500": (500, 4.00)}
    for k, v in pkgs.items():
        builder.button(text=f"{v[0]} {t_name} — {v[1]} USDT", callback_data=f"buy_{k}")
    return builder.adjust(1).as_markup()

# ==================== ХЕНДЛЕРЫ ====================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    ref_id = int(args[1].replace("ref", "")) if len(args) > 1 and args[1].startswith("ref") else None
    
    with sqlite3.connect('users.db') as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date, referred_by) VALUES (?, ?, ?, datetime('now'), ?)",
                     (user_id, message.from_user.username, message.from_user.first_name, ref_id))
    
    bot_info = await bot.get_me()
    lang = get_user_lang(user_id)

    if len(args) > 1 and args[1] == "deposit":
        await message.answer(BOT_TEXTS[lang]['dep_notif'], reply_markup=packages_keyboard(lang))
        return

    await message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(user_id, bot_info.username))

# Фильтры кнопок (работают на всех языках)
@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['buy'] for l in BOT_TEXTS))
async def buy_handler(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(BOT_TEXTS[lang]['buy_menu'], reply_markup=packages_keyboard(lang), parse_mode="Markdown")

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['stats'] for l in BOT_TEXTS))
async def stats_handler(message: Message):
    lang = get_user_lang(message.from_user.id)
    _, coins = get_user_stats(message.from_user.id)
    await message.answer(BOT_TEXTS[lang]['balance_text'].format(c=coins))

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['ref'] for l in BOT_TEXTS))
async def ref_handler(message: Message):
    lang = get_user_lang(message.from_user.id)
    bot_info = await bot.get_me()
    cnt, _ = get_user_stats(message.from_user.id)
    await message.answer(BOT_TEXTS[lang]['ref_text'].format(b=bot_info.username, u=message.from_user.id, cnt=cnt))

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['settings'] for l in BOT_TEXTS))
async def settings_handler(message: Message):
    builder = InlineKeyboardBuilder()
    for code, name in LANGUAGES.items():
        builder.button(text=name, callback_data=f"sl_{code}")
    await message.answer("Choose language / Wybierz język:", reply_markup=builder.adjust(2).as_markup())

@dp.callback_query(F.data.startswith("sl_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, call.from_user.id))
    bot_info = await bot.get_me()
    await call.message.edit_text(BOT_TEXTS[lang]['lang_ok'])
    await call.message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(call.from_user.id, bot_info.username))

# ==================== API ДЛЯ MINI APP ====================
async def api_get_balance(request: web.Request) -> web.Response:
    try:
        init_data = request.rel_url.query.get("init_data", "")
        parsed = dict(urllib.parse.parse_qsl(init_data))
        user_id = json.loads(parsed.get("user", "{}")).get("id")
        _, coins = get_user_stats(user_id)
        return web.json_response({"ok": True, "balance": coins}, headers={"Access-Control-Allow-Origin": "*"})
    except: return web.json_response({"ok": False}, status=400)

async def api_spin(request: web.Request) -> web.Response:
    try:
        body = await request.json()
        parsed = dict(urllib.parse.parse_qsl(body.get("init_data", "")))
        user_id = json.loads(parsed.get("user", "{}")).get("id")
        bet, win = int(body.get("bet", 0)), int(body.get("winnings", 0))
        with sqlite3.connect('users.db') as conn:
            curr = conn.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
            if curr < bet: return web.json_response({"ok": False, "error": "No money"})
            new_bal = curr - bet + win
            conn.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_bal, user_id))
        return web.json_response({"ok": True, "balance": new_bal}, headers={"Access-Control-Allow-Origin": "*"})
    except: return web.json_response({"ok": False}, status=400)

async def start_api_server():
    app = web.Application()
    app.router.add_get("/api/balance", api_get_balance)
    app.router.add_post("/api/spin", api_spin)
    app.router.add_options("/{tail:.*}", lambda r: web.Response(headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"}))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", API_PORT).start()

# ==================== ЗАПУСК ====================
async def main():
    init_db()
    asyncio.create_task(start_api_server())
    print(f"🚀 Бот запущен на порту {API_PORT}")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
