import logging, sqlite3, asyncio, os, json, urllib.parse
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# ==================== НАСТРОЙКИ ====================
load_dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(load_dotenv_path):
    from dotenv import load_dotenv
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_PORT = int(os.getenv("PORT", 8081))
PUBLIC_API_URL = f"https://{os.getenv('RAILWAY_STATIC_URL', 'lucky-slots-production.up.railway.app')}"

# ==================== ЛОКАЛИЗАЦИЯ ====================
LANGUAGES = {'pl': '🇵🇱 Polski', 'ua': '🇺🇦 Українська', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
BOT_TEXTS = {
    'pl': {
        'welcome': 'Witaj w Lucky Slots! 🎰', 'play': '🎰 Graj teraz', 'buy': '💳 Kup żetony', 'set': '⚙️ Język', 'bal': '💰 Баланс', 'ref': '👥 Poleć znajomego',
        'balance_text': 'Twój balans: {c} żetonów', 'dep_notif': '💳 Wybierz pakiet żetonów do doładowania:', 'lang_ok': '✅ Język zmieniony!', 'token': 'żetonów',
        'ref_text': '🔗 Twoja link (kliknij, aby skopiować):\n<code>https://t.me/{b}?start=ref{u}</code>\n\n👥 Poleceni: {cnt}', 'buy_menu': '💳 *Wybierz pakiet:*'
    },
    'ua': {
        'welcome': 'Вітаємо у Lucky Slots! 🎰', 'play': '🎰 Грати зараз', 'buy': '💳 Купити жетони', 'set': '⚙️ Мова', 'bal': '💰 Баланс', 'ref': '👥 Запросити друга',
        'balance_text': 'Ваш баланс: {c} жетонів', 'dep_notif': '💳 Оберіть пакет жетонів для поповнення:', 'lang_ok': '✅ Мову змінено!', 'token': 'жетонів',
        'ref_text': '🔗 Посилання (натисніть, щоб скопіювати):\n<code>https://t.me/{b}?start=ref{u}</code>\n\n👥 Запрошено: {cnt}', 'buy_menu': '💳 *Оберіть пакет:*'
    },
    'ru': {
        'welcome': 'Добро пожаловать в Lucky Slots! 🎰', 'play': '🎰 Играть сейчас', 'buy': '💳 Купить жетоны', 'set': '⚙️ Язык', 'bal': '💰 Баланс', 'ref': '👥 Рефералы',
        'balance_text': 'Ваш баланс: {c} жетонов', 'dep_notif': '💳 Выберите пакет жетонов для пополнения:', 'lang_ok': '✅ Язык изменен!', 'token': 'жетонов',
        'ref_text': '🔗 Ссылка (нажми, чтобы скопировать):\n<code>https://t.me/{b}?start=ref{u}</code>\n\n👥 Рефералов: {cnt}', 'buy_menu': '💳 *Выберите пакет:*'
    },
    'en': {
        'welcome': 'Welcome to Lucky Slots! 🎰', 'play': '🎰 Play Now', 'buy': '💳 Buy Coins', 'set': '⚙️ Language', 'bal': '💰 Balance', 'ref': '👥 Referrals',
        'balance_text': 'Your balance: {c} coins', 'dep_notif': '💳 Choose a package to deposit:', 'lang_ok': '✅ Language changed!', 'token': 'coins',
        'ref_text': '🔗 Your link (tap to copy):\n<code>https://t.me/{b}?start=ref{u}</code>\n\n👥 Referrals: {cnt}', 'buy_menu': '💳 *Choose a package:*'
    }
}

# ==================== БД ====================
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, referrals_count INTEGER DEFAULT 0, coins INTEGER DEFAULT 0, language TEXT DEFAULT 'pl')")
        try: conn.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'pl'")
        except: pass

def get_user_data(user_id):
    with sqlite3.connect('users.db') as conn:
        res = conn.execute("SELECT language, coins, referrals_count FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return res if res else ('pl', 0, 0)

# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id, bot_name):
    lang, _, _ = get_user_data(user_id)
    t = BOT_TEXTS[lang]
    webapp_url = f"https://evgeniyzno1998-ship-it.github.io/lucky-slots/?api={PUBLIC_API_URL}&bot={bot_name}&lang={lang}"
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t['play'], web_app=WebAppInfo(url=webapp_url))],
        [KeyboardButton(text=t['buy']), KeyboardButton(text=t['bal'])],
        [KeyboardButton(text=t['ref']), KeyboardButton(text=t['set'])]
    ], resize_keyboard=True)

def packages_keyboard(lang):
    t_name = BOT_TEXTS[lang]['token']
    builder = InlineKeyboardBuilder()
    pkgs = {"50": 0.50, "100": 0.90, "500": 4.00}
    for label, price in pkgs.items():
        builder.button(text=f"{label} {t_name} — {price} USDT", callback_data=f"buy_{label}")
    return builder.adjust(1).as_markup()

# ==================== ХЕНДЛЕРЫ ====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    ref_id = int(args[1].replace("ref", "")) if len(args) > 1 and args[1].startswith("ref") else None
    
    with sqlite3.connect('users.db') as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, language) VALUES (?, ?, ?, 'pl')", (user_id, message.from_user.username, message.from_user.first_name))
        if ref_id and ref_id != user_id:
            conn.execute("UPDATE users SET referrals_count = referrals_count + 1, coins = coins + 10 WHERE user_id = ?", (ref_id,))
    
    bot_info = await bot.get_me()
    lang, _, _ = get_user_data(user_id)
    if len(args) > 1 and args[1] == "deposit":
        await message.answer(BOT_TEXTS[lang]['dep_notif'], reply_markup=packages_keyboard(lang))
        return
    await message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(user_id, bot_info.username))

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['buy'] for l in BOT_TEXTS))
async def buy_btn(message: Message):
    lang = get_user_lang(message.from_user.id)
    await message.answer(BOT_TEXTS[lang]['buy_menu'], reply_markup=packages_keyboard(lang), parse_mode="Markdown")

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['bal'] for l in BOT_TEXTS))
async def bal_btn(message: Message):
    lang, coins, _ = get_user_data(message.from_user.id)
    await message.answer(BOT_TEXTS[lang]['balance_text'].format(c=coins))

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['ref'] for l in BOT_TEXTS))
async def ref_btn(message: Message):
    lang, _, refs = get_user_data(message.from_user.id)
    bot_info = await bot.get_me()
    await message.answer(BOT_TEXTS[lang]['ref_text'].format(b=bot_info.username, u=message.from_user.id, cnt=refs), parse_mode="HTML")

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['set'] for l in BOT_TEXTS))
async def lang_btn(message: Message):
    builder = InlineKeyboardBuilder()
    for code, name in LANGUAGES.items(): builder.button(text=name, callback_data=f"sl_{code}")
    await message.answer("Choose language:", reply_markup=builder.adjust(2).as_markup())

@dp.callback_query(F.data.startswith("sl_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, call.from_user.id))
    bot_info = await bot.get_me()
    await call.message.edit_text(BOT_TEXTS[lang]['lang_ok'])
    await call.message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(call.from_user.id, bot_info.username))

# ==================== API ====================
async def api_get_balance(request: web.Request) -> web.Response:
    try:
        init_data = request.rel_url.query.get("init_data", "")
        parsed = dict(urllib.parse.parse_qsl(init_data))
        user_id = json.loads(parsed.get("user", "{}")).get("id")
        _, coins, _ = get_user_data(user_id)
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

async def main():
    init_db()
    asyncio.create_task(start_api_server())
    await dp.start_polling(bot)

if __name__ == '__main__': asyncio.run(main())
