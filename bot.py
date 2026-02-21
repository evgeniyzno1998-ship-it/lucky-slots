import logging, sqlite3, asyncio, os, json, urllib.parse, hashlib, hmac
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# ==================== НАСТРОЙКИ ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Убедись, что в Railway в переменных PUBLIC_URL стоит адрес вида https://lucky-slots-production.up.railway.app
API_URL = os.getenv("PUBLIC_URL", "https://lucky-slots-production.up.railway.app")
API_PORT = int(os.getenv("PORT", 8081))

# ==================== ЛОКАЛИЗАЦИЯ ====================
LANGUAGES = {'pl': '🇵🇱 Polski', 'ua': '🇺🇦 Українська', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
BOT_TEXTS = {
    'pl': {'welcome': 'Witaj w Lucky Slots! 🎰', 'play': '🎰 Graj teraz', 'buy': '💳 Kup żetony', 'set': '⚙️ Język', 'bal': '💰 Moje żetony', 'ref': '👥 Poleć znajomego', 'lang_ok': '✅ Język zmieniony!', 'token': 'żetonów', 'ref_t': '🔗 Link (kliknij aby skopiować):\n<code>https://t.me/{b}?start=ref{u}</code>\n👥 Poleceni: {cnt}'},
    'ua': {'welcome': 'Вітаємо у Lucky Slots! 🎰', 'play': '🎰 Грати зараз', 'buy': '💳 Купити жетони', 'set': '⚙️ Мова', 'bal': '💰 Мій баланс', 'ref': '👥 Запросити друга', 'lang_ok': '✅ Мову змінено!', 'token': 'жетонів', 'ref_t': '🔗 Посилання (натисніть щоб скопіювати):\n<code>https://t.me/{b}?start=ref{u}</code>\n👥 Запрошено: {cnt}'},
    'ru': {'welcome': 'Добро пожаловать в Lucky Slots! 🎰', 'play': '🎰 Играть сейчас', 'buy': '💳 Купить жетоны', 'set': '⚙️ Язык', 'bal': '💰 Мой баланс', 'ref': '👥 Рефералы', 'lang_ok': '✅ Язык изменен!', 'token': 'жетонов', 'ref_t': '🔗 Ссылка (нажми чтобы скопировать):\n<code>https://t.me/{b}?start=ref{u}</code>\n👥 Рефералов: {cnt}'},
    'en': {'welcome': 'Welcome to Lucky Slots! 🎰', 'play': '🎰 Play Now', 'buy': '💳 Buy Coins', 'set': '⚙️ Language', 'bal': '💰 My Balance', 'ref': '👥 Referrals', 'lang_ok': '✅ Language changed!', 'token': 'coins', 'ref_t': '🔗 Link (tap to copy):\n<code>https://t.me/{b}?start=ref{u}</code>\n👥 Referrals: {cnt}'}
}

# ==================== БАЗА ДАННЫХ ====================
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
    webapp_url = f"https://evgeniyzno1998-ship-it.github.io/lucky-slots/?api={API_URL}&bot={bot_name}&lang={lang}"
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t['play'], web_app=WebAppInfo(url=webapp_url))],
        [KeyboardButton(text=t['buy']), KeyboardButton(text=t['bal'])],
        [KeyboardButton(text=t['ref']), KeyboardButton(text=t['set'])]
    ], resize_keyboard=True)

def pkgs_kb(lang):
    t_n = BOT_TEXTS[lang]['token']
    builder = InlineKeyboardBuilder()
    for l, p in {"50": 0.50, "100": 0.90, "500": 4.00}.items():
        builder.button(text=f"{l} {t_n} — {p} USDT", callback_data=f"buy_{l}")
    return builder.adjust(1).as_markup()

# ==================== ХЕНДЛЕРЫ ====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    with sqlite3.connect('users.db') as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", (user_id, message.from_user.username, message.from_user.first_name))
    
    bot_info = await bot.get_me()
    lang, _, _ = get_user_data(user_id)
    if len(args) > 1 and args[1] == "deposit":
        await message.answer(BOT_TEXTS[lang]['buy'], reply_markup=pkgs_kb(lang))
        return
    await message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(user_id, bot_info.username))

# Универсальный хендлер для всех кнопок (исправляет проблему распознавания)
@dp.message(F.text)
async def universal_handler(message: Message):
    uid = message.from_user.id
    lang, coins, refs = get_user_data(uid)
    txt = message.text
    b_info = await bot.get_me()

    if any(txt == BOT_TEXTS[l]['buy'] for l in BOT_TEXTS):
        await message.answer(BOT_TEXTS[lang]['buy'], reply_markup=pkgs_kb(lang))
    elif any(txt == BOT_TEXTS[l]['bal'] for l in BOT_TEXTS):
        await message.answer(BOT_TEXTS[lang]['balance_text'].format(c=coins))
    elif any(txt == BOT_TEXTS[l]['ref'] for l in BOT_TEXTS):
        await message.answer(BOT_TEXTS[lang]['ref_t'].format(b=b_info.username, u=uid, cnt=refs), parse_mode="HTML")
    elif any(txt == BOT_TEXTS[l]['set'] for l in BOT_TEXTS):
        builder = InlineKeyboardBuilder()
        for c, n in LANGUAGES.items(): builder.button(text=n, callback_data=f"sl_{c}")
        await message.answer("Language:", reply_markup=builder.adjust(2).as_markup())

@dp.callback_query(F.data.startswith("sl_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, call.from_user.id))
    b_info = await bot.get_me()
    await call.message.edit_text(BOT_TEXTS[lang]['lang_ok'])
    await call.message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(call.from_user.id, b_info.username))

# ==================== API (С ПРОВЕРКОЙ CORS) ====================
async def api_get_balance(request):
    try:
        init_data = request.rel_url.query.get("init_data", "")
        parsed = dict(urllib.parse.parse_qsl(init_data))
        user_id = json.loads(parsed.get("user")).get("id")
        _, coins, _ = get_user_data(user_id)
        return web.json_response({"ok": True, "balance": coins}, headers={"Access-Control-Allow-Origin": "*"})
    except: return web.json_response({"ok": False}, headers={"Access-Control-Allow-Origin": "*"})

async def api_spin(request):
    if request.method == "OPTIONS": return web.Response(headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "*"})
    try:
        data = await request.json()
        parsed = dict(urllib.parse.parse_qsl(data.get("init_data")))
        uid = json.loads(parsed.get("user")).get("id")
        bet, win = int(data.get("bet")), int(data.get("winnings"))
        with sqlite3.connect('users.db') as conn:
            cur_bal = conn.execute("SELECT coins FROM users WHERE user_id = ?", (uid,)).fetchone()[0]
            if cur_bal < bet: return web.json_response({"ok": False, "error": "No balance"}, headers={"Access-Control-Allow-Origin": "*"})
            new_bal = cur_bal - bet + win
            conn.execute("UPDATE users SET coins = ? WHERE user_id = ?", (new_bal, uid))
        return web.json_response({"ok": True, "balance": new_bal}, headers={"Access-Control-Allow-Origin": "*"})
    except: return web.json_response({"ok": False}, headers={"Access-Control-Allow-Origin": "*"})

async def start_api():
    app = web.Application()
    app.router.add_get("/api/balance", api_get_balance)
    app.router.add_post("/api/spin", api_spin)
    app.router.add_options("/{tail:.*}", lambda r: web.Response(headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"}))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", API_PORT).start()

async def main():
    init_db()
    asyncio.create_task(start_api())
    await dp.start_polling(bot)

if __name__ == '__main__': asyncio.run(main())
