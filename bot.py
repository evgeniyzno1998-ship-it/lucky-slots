import logging, sqlite3, asyncio, os, json, urllib.parse
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN")
# ВАЖНО: Укажи тут свой реальный публичный адрес Railway (https://xxx.up.railway.app)
PUBLIC_API_URL = "https://lucky-slots-production.up.railway.app"
API_PORT = int(os.getenv("PORT", 8081))

# Локализация
LANGUAGES = {'pl': '🇵🇱 Polski', 'ua': '🇺🇦 Українська', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
BOT_TEXTS = {
    'pl': {
        'welcome': 'Witaj w Lucky Slots! 🎰', 'play': '🎰 Graj teraz', 'buy': '💳 Kup żetony', 'set': '⚙️ Język', 'bal': '💰 Баланс', 'ref': '👥 Poleć znajomego',
        'balance_text': 'Twój balans: {c} żetonów', 'dep_notif': 'Brak żetonów! Wybierz pakiet:', 'lang_ok': '✅ Język zmieniony!', 'token': 'żetonów',
        'ref_text': '🔗 Twoja link (kliknij, aby skopiować):\n`https://t.me/{b}?start=ref{u}`\n\n👥 Poleceni: {cnt}'
    },
    'ua': {
        'welcome': 'Вітаємо у Lucky Slots! 🎰', 'play': '🎰 Грати зараз', 'buy': '💳 Купити жетони', 'set': '⚙️ Мова', 'bal': '💰 Баланс', 'ref': '👥 Запросити друга',
        'balance_text': 'Ваш баланс: {c} жетонів', 'dep_notif': 'Немає жетонів! Оберіть пакет:', 'lang_ok': '✅ Мову змінено!', 'token': 'жетонів',
        'ref_text': '🔗 Ваше посилання (натисніть, щоб скопіювати):\n`https://t.me/{b}?start=ref{u}`\n\n👥 Запрошено: {cnt}'
    },
    'ru': {
        'welcome': 'Добро пожаловать в Lucky Slots! 🎰', 'play': '🎰 Играть сейчас', 'buy': '💳 Купить жетоны', 'set': '⚙️ Язык', 'bal': '💰 Баланс', 'ref': '👥 Рефералы',
        'balance_text': 'Ваш баланс: {c} жетонов', 'dep_notif': 'Нет жетонов! Выберите пакет:', 'lang_ok': '✅ Язык изменен!', 'token': 'жетонов',
        'ref_text': '🔗 Ваша ссылка (нажми, чтобы скопировать):\n`https://t.me/{b}?start=ref{u}`\n\n👥 Рефералов: {cnt}'
    },
    'en': {
        'welcome': 'Welcome to Lucky Slots! 🎰', 'play': '🎰 Play Now', 'buy': '💳 Buy Coins', 'set': '⚙️ Language', 'bal': '💰 Balance', 'ref': '👥 Referrals',
        'balance_text': 'Your balance: {c} coins', 'dep_notif': 'No coins! Choose a package:', 'lang_ok': '✅ Language changed!', 'token': 'coins',
        'ref_text': '🔗 Your link (tap to copy):\n`https://t.me/{b}?start=ref{u}`\n\n👥 Referrals: {cnt}'
    }
}

# БД функции
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, referrals_count INTEGER DEFAULT 0, coins INTEGER DEFAULT 0, language TEXT DEFAULT 'pl')")
        try: conn.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'pl'")
        except: pass

def get_user_data(user_id):
    with sqlite3.connect('users.db') as conn:
        return conn.execute("SELECT language, coins, referrals_count FROM users WHERE user_id = ?", (user_id,)).fetchone() or ('pl', 0, 0)

def main_menu(user_id, bot_name):
    lang, _, _ = get_user_data(user_id)
    t = BOT_TEXTS[lang]
    webapp_url = f"https://evgeniyzno1998-ship-it.github.io/lucky-slots/?api={PUBLIC_API_URL}&bot={bot_name}&lang={lang}"
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t['play'], web_app=WebAppInfo(url=webapp_url))],
        [KeyboardButton(text=t['buy']), KeyboardButton(text=t['bal'])],
        [KeyboardButton(text=t['ref']), KeyboardButton(text=t['set'])]
    ], resize_keyboard=True)

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
        await message.answer(BOT_TEXTS[lang]['dep_notif']) # Здесь можно добавить кнопки оплаты
        return

    await message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(user_id, bot_info.username))

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['set'] for l in BOT_TEXTS))
async def cmd_lang(message: Message):
    builder = InlineKeyboardBuilder()
    for code, name in LANGUAGES.items(): builder.button(text=name, callback_data=f"sl_{code}")
    await message.answer("Select language:", reply_markup=builder.adjust(2).as_markup())

@dp.callback_query(F.data.startswith("sl_"))
async def set_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, call.from_user.id))
    bot_info = await bot.get_me()
    await call.message.edit_text(BOT_TEXTS[lang]['lang_ok'])
    await call.message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(call.from_user.id, bot_info.username))

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['bal'] for l in BOT_TEXTS))
async def cmd_bal(message: Message):
    lang, coins, _ = get_user_data(message.from_user.id)
    await message.answer(BOT_TEXTS[lang]['balance_text'].format(c=coins))

@dp.message(lambda m: any(m.text == BOT_TEXTS[l]['ref'] for l in BOT_TEXTS))
async def cmd_ref(message: Message):
    lang, _, refs = get_user_data(message.from_user.id)
    bot_info = await bot.get_me()
    await message.answer(BOT_TEXTS[lang]['ref_text'].format(b=bot_info.username, u=message.from_user.id, cnt=refs), parse_mode="MarkdownV2")

# ==================== API ДЛЯ ИГРЫ ====================
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
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", API_PORT).start()

async def main():
    init_db()
    asyncio.create_task(start_api_server())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
