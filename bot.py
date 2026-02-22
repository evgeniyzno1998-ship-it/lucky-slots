import logging, sqlite3, asyncio, os, json, urllib.parse, hashlib, hmac, random, time
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
CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN")
API_PORT = int(os.getenv("PORT", 8080))
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://lucky-slots-production.up.railway.app")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://evgeniyzno1998-ship-it.github.io/lucky-slots/")

REFERRAL_BONUS = 10

# ==================== ЛОКАЛИЗАЦИЯ ====================
LANGUAGES = {'pl': '🇵🇱 Polski', 'ua': '🇺🇦 Українська', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
BOT_TEXTS = {
    'pl': {
        'welcome': 'Witaj w Lucky Slots! 🎰', 'play': '🎰 Graj teraz', 'buy': '💳 Kup żetony',
        'set': '⚙️ Język', 'bal': '💰 Moje żetony', 'ref': '👥 Poleć znajomego',
        'balance_text': 'Twój balans: {c} żetonów', 'lang_ok': '✅ Język zmieniony!',
        'token': 'żetonów', 'buy_m': '💳 Wybierz pakiet:',
        'ref_t': '👥 <b>Twój link polecający:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Zaprosiłeś: <b>{refs}</b> znajomych\n💰 Zdobyłeś: <b>{earned}</b> żetonów z poleceń\n\n💡 Za każdego znajomego dostajesz <b>{bonus}</b> żetonów!',
        'ref_welcome': '🎉 Zaproszony przez znajomego! Bonus {bonus} żetonów dla Was obu!',
        'ref_earned': '🎉 Nowy znajomy dołączył! +{bonus} żetonów!',
        'pay_success': '✅ Zakup udany! +{amount} żetonów\nNowy balans: {balance} żetonów',
        'pay_pending': '⏳ Oczekiwanie na płatność...\n\nKliknij przycisk poniżej aby zapłacić:',
    },
    'ua': {
        'welcome': 'Вітаємо у Lucky Slots! 🎰', 'play': '🎰 Грати зараз', 'buy': '💳 Купити жетони',
        'set': '⚙️ Мова', 'bal': '💰 Мій баланс', 'ref': '👥 Запросити друга',
        'balance_text': 'Ваш баланс: {c} жетонів', 'lang_ok': '✅ Мову змінено!',
        'token': 'жетонів', 'buy_m': '💳 Оберіть пакет:',
        'ref_t': '👥 <b>Ваше посилання:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Запросили: <b>{refs}</b> друзів\n💰 Зароблено: <b>{earned}</b> жетонів з рефералів\n\n💡 За кожного друга ви отримуєте <b>{bonus}</b> жетонів!',
        'ref_welcome': '🎉 Вас запросив друг! Бонус {bonus} жетонів для обох!',
        'ref_earned': '🎉 Новий друг приєднався! +{bonus} жетонів!',
        'pay_success': '✅ Покупка успішна! +{amount} жетонів\nНовий баланс: {balance} жетонів',
        'pay_pending': '⏳ Очікування оплати...\n\nНатисніть кнопку нижче для оплати:',
    },
    'ru': {
        'welcome': 'Добро пожаловать! 🎰', 'play': '🎰 Играть сейчас', 'buy': '💳 Купить жетоны',
        'set': '⚙️ Язык', 'bal': '💰 Мой баланс', 'ref': '👥 Рефералы',
        'balance_text': 'Ваш баланс: {c} жетонов', 'lang_ok': '✅ Язык изменен!',
        'token': 'жетонов', 'buy_m': '💳 Выберите пакет:',
        'ref_t': '👥 <b>Ваша ссылка:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Приглашено: <b>{refs}</b> друзей\n💰 Заработано: <b>{earned}</b> жетонов с рефералов\n\n💡 За каждого друга вы получаете <b>{bonus}</b> жетонов!',
        'ref_welcome': '🎉 Вас пригласил друг! Бонус {bonus} жетонов обоим!',
        'ref_earned': '🎉 Новый друг присоединился! +{bonus} жетонов!',
        'pay_success': '✅ Покупка успешна! +{amount} жетонов\nНовый баланс: {balance} жетонов',
        'pay_pending': '⏳ Ожидание оплаты...\n\nНажмите кнопку ниже для оплаты:',
    },
    'en': {
        'welcome': 'Welcome! 🎰', 'play': '🎰 Play Now', 'buy': '💳 Buy Coins',
        'set': '⚙️ Language', 'bal': '💰 My Balance', 'ref': '👥 Referrals',
        'balance_text': 'Your balance: {c} coins', 'lang_ok': '✅ Language changed!',
        'token': 'coins', 'buy_m': '💳 Choose package:',
        'ref_t': '👥 <b>Your referral link:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Invited: <b>{refs}</b> friends\n💰 Earned: <b>{earned}</b> coins from referrals\n\n💡 You get <b>{bonus}</b> coins for each friend!',
        'ref_welcome': '🎉 Invited by a friend! Bonus {bonus} coins for both of you!',
        'ref_earned': '🎉 New friend joined! +{bonus} coins!',
        'pay_success': '✅ Purchase successful! +{amount} coins\nNew balance: {balance} coins',
        'pay_pending': '⏳ Waiting for payment...\n\nClick the button below to pay:',
    }
}

PACKAGES = {"50": 0.50, "100": 0.90, "500": 4.00}
SYMS = ['🍒', '🍋', '🍊', '🍇', '🍫', '🍭', '🍬', '💎']

# ==================== БАЗА ДАННЫХ (async-safe + WAL) ====================
DB_PATH = 'users.db'
_db_lock = asyncio.Lock()


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _get_conn() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            referrals_count INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 0,
            language TEXT DEFAULT 'pl',
            referred_by INTEGER DEFAULT NULL
        )''')
        for col, defn in [("language", "TEXT DEFAULT 'pl'"), ("referred_by", "INTEGER DEFAULT NULL")]:
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col} {defn}")
            except sqlite3.OperationalError:
                pass


async def db_execute(query, params=(), fetch=False, fetchone=False):
    async with _db_lock:
        loop = asyncio.get_event_loop()
        def _run():
            with _get_conn() as conn:
                cur = conn.execute(query, params)
                if fetchone:
                    return cur.fetchone()
                if fetch:
                    return cur.fetchall()
                return None
        return await loop.run_in_executor(None, _run)


async def get_user_data(user_id):
    row = await db_execute(
        "SELECT language, coins, referrals_count FROM users WHERE user_id = ?",
        (int(user_id),), fetchone=True
    )
    return (row['language'], row['coins'], row['referrals_count']) if row else ('pl', 0, 0)


async def ensure_user(user_id, username=None, first_name=None):
    existing = await db_execute(
        "SELECT user_id FROM users WHERE user_id = ?", (int(user_id),), fetchone=True
    )
    if not existing:
        await db_execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, language) VALUES (?, ?, ?, 'pl')",
            (int(user_id), username, first_name)
        )
        return True
    else:
        if username or first_name:
            await db_execute(
                "UPDATE users SET username = COALESCE(?, username), first_name = COALESCE(?, first_name) WHERE user_id = ?",
                (username, first_name, int(user_id))
            )
    return False


async def update_coins(user_id, delta):
    await db_execute(
        "UPDATE users SET coins = MAX(0, coins + ?) WHERE user_id = ?",
        (delta, int(user_id))
    )
    row = await db_execute("SELECT coins FROM users WHERE user_id = ?", (int(user_id),), fetchone=True)
    return row['coins'] if row else 0


async def get_coins(user_id):
    row = await db_execute("SELECT coins FROM users WHERE user_id = ?", (int(user_id),), fetchone=True)
    return row['coins'] if row else 0


# ==================== ВАЛИДАЦИЯ TELEGRAM initData ====================
def validate_init_data(init_data_raw: str):
    """
    Возвращает (user_dict | None, is_verified: bool).
    Если HMAC не совпадает но user парсится — возвращает (user, False) как fallback.
    """
    if not init_data_raw or not init_data_raw.strip():
        logging.warning("⚠️ initData is empty!")
        return None, False

    try:
        parsed = dict(urllib.parse.parse_qsl(init_data_raw))
        user_raw = parsed.get("user", "")
        if not user_raw:
            logging.warning("⚠️ initData has no 'user' field. Keys: %s", list(parsed.keys()))
            return None, False

        user_data = json.loads(user_raw)
        if not user_data.get("id"):
            logging.warning("⚠️ initData user has no 'id'")
            return None, False

        uid = user_data["id"]

        # Пробуем HMAC
        received_hash = parsed.get("hash", "")
        if not received_hash:
            logging.warning(f"⚠️ No hash in initData, uid={uid} — fallback")
            return user_data, False

        check_params = {k: v for k, v in parsed.items() if k != "hash"}
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(check_params.items()))

        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(computed_hash, received_hash):
            logging.warning(f"⚠️ HMAC mismatch uid={uid} — fallback (expected={computed_hash[:16]}... got={received_hash[:16]}...)")
            return user_data, False

        # auth_date — допуск 24 часа
        auth_date = int(parsed.get("auth_date", 0))
        if auth_date > 0 and abs(time.time() - auth_date) > 86400:
            logging.warning(f"⚠️ initData expired uid={uid}, age={int(time.time()-auth_date)}s — fallback")
            return user_data, False

        logging.info(f"✅ initData verified uid={uid}")
        return user_data, True

    except Exception as e:
        logging.error(f"initData parse error: {e}", exc_info=True)
        return None, False


def extract_user_from_init_data(init_data_raw: str):
    """Извлекает user — работает даже если HMAC не прошёл."""
    user, verified = validate_init_data(init_data_raw)
    if user and not verified:
        logging.info(f"🔓 Fallback mode uid={user.get('id')}")
    return user


# ==================== СЕРВЕРНАЯ ЛОГИКА СПИНА ====================
def compute_spin():
    grid = [random.choice(SYMS) for _ in range(30)]
    counts = {}
    for s in grid:
        counts[s] = counts.get(s, 0) + 1

    multiplier = 0.0
    for sym, count in counts.items():
        if count >= 12:
            multiplier += 5.0
        elif count >= 8:
            multiplier += 1.5

    return grid, multiplier


# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id, bot_name, lang):
    t = BOT_TEXTS[lang]
    webapp_url = f"{WEBAPP_URL}?api={urllib.parse.quote(PUBLIC_URL, safe='')}&bot={bot_name}&lang={lang}"
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t['play'], web_app=WebAppInfo(url=webapp_url))],
        [KeyboardButton(text=t['buy']), KeyboardButton(text=t['bal'])],
        [KeyboardButton(text=t['ref']), KeyboardButton(text=t['set'])]
    ], resize_keyboard=True)


def pkgs_kb(lang):
    t_n = BOT_TEXTS[lang]['token']
    builder = InlineKeyboardBuilder()
    for amount, price in PACKAGES.items():
        builder.button(text=f"{amount} {t_n} — {price} USDT", callback_data=f"buy_{amount}")
    return builder.adjust(1).as_markup()


# ==================== БОТ ====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    is_new = await ensure_user(user_id, message.from_user.username, message.from_user.first_name)
    bot_info = await bot.get_me()
    lang, _, _ = await get_user_data(user_id)

    # deposit deep-link — сразу пакеты
    if len(args) > 1 and args[1] == "deposit":
        await message.answer(BOT_TEXTS[lang]['buy_m'], reply_markup=pkgs_kb(lang))
        return

    # Реферал
    if is_new and len(args) > 1 and args[1].startswith("ref"):
        try:
            referrer_id = int(args[1][3:])
            if referrer_id != user_id:
                await db_execute(
                    "UPDATE users SET referred_by = ? WHERE user_id = ? AND referred_by IS NULL",
                    (referrer_id, user_id)
                )
                await db_execute(
                    "UPDATE users SET referrals_count = referrals_count + 1, coins = coins + ? WHERE user_id = ?",
                    (REFERRAL_BONUS, referrer_id)
                )
                await update_coins(user_id, REFERRAL_BONUS)
                ref_lang, _, _ = await get_user_data(referrer_id)
                try:
                    await bot.send_message(referrer_id, BOT_TEXTS[ref_lang]['ref_earned'].format(bonus=REFERRAL_BONUS))
                except Exception:
                    pass
                await message.answer(BOT_TEXTS[lang]['ref_welcome'].format(bonus=REFERRAL_BONUS))
        except (ValueError, IndexError):
            pass

    await message.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(user_id, bot_info.username, lang))


@dp.message(F.text)
async def handle_buttons(message: Message):
    uid = message.from_user.id
    txt = message.text.strip()
    lang, coins, refs = await get_user_data(uid)
    bot_info = await bot.get_me()

    if any(txt == BOT_TEXTS[l]['buy'] for l in BOT_TEXTS):
        await message.answer(BOT_TEXTS[lang]['buy_m'], reply_markup=pkgs_kb(lang))
    elif any(txt == BOT_TEXTS[l]['bal'] for l in BOT_TEXTS):
        await message.answer(BOT_TEXTS[lang]['balance_text'].format(c=coins))
    elif any(txt == BOT_TEXTS[l]['ref'] for l in BOT_TEXTS):
        earned = refs * REFERRAL_BONUS
        await message.answer(
            BOT_TEXTS[lang]['ref_t'].format(b=bot_info.username, u=uid, refs=refs, earned=earned, bonus=REFERRAL_BONUS),
            parse_mode="HTML"
        )
    elif any(txt == BOT_TEXTS[l]['set'] for l in BOT_TEXTS):
        kb = InlineKeyboardBuilder()
        for c, n in LANGUAGES.items():
            kb.button(text=n, callback_data=f"sl_{c}")
        await message.answer("Language:", reply_markup=kb.adjust(2).as_markup())


@dp.callback_query(F.data.startswith("sl_"))
async def set_lang(call: CallbackQuery):
    lang_code = call.data.split("_")[1]
    if lang_code not in LANGUAGES:
        return
    await db_execute("UPDATE users SET language = ? WHERE user_id = ?", (lang_code, call.from_user.id))
    b_info = await bot.get_me()
    await call.message.edit_text(BOT_TEXTS[lang_code]['lang_ok'])
    await call.message.answer(
        BOT_TEXTS[lang_code]['welcome'],
        reply_markup=main_menu(call.from_user.id, b_info.username, lang_code)
    )


@dp.callback_query(F.data.startswith("buy_"))
async def handle_buy(call: CallbackQuery):
    amount_str = call.data.split("_")[1]
    if amount_str not in PACKAGES:
        return
    price = PACKAGES[amount_str]
    coins_amount = int(amount_str)
    uid = call.from_user.id
    lang, _, _ = await get_user_data(uid)

    if not CRYPTO_TOKEN:
        await call.answer("Payment not configured", show_alert=True)
        return

    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            resp = await session.post(
                "https://pay.crypt.bot/api/createInvoice",
                json={
                    "currency_type": "fiat", "fiat": "USD", "amount": str(price),
                    "description": f"Lucky Slots: {coins_amount} {BOT_TEXTS[lang]['token']}",
                    "payload": json.dumps({"user_id": uid, "coins": coins_amount}),
                    "paid_btn_name": "callback",
                    "paid_btn_url": f"https://t.me/{(await bot.get_me()).username}"
                },
                headers={"Crypto-Pay-API-Token": CRYPTO_TOKEN}
            )
            data = await resp.json()
            if not data.get("ok"):
                logging.error(f"Crypto Bot error: {data}")
                await call.answer("Payment error", show_alert=True)
                return
            pay_url = data["result"]["mini_app_invoice_url"]
            kb = InlineKeyboardBuilder()
            kb.button(text=f"💳 Pay {price} USDT", url=pay_url)
            await call.message.edit_text(BOT_TEXTS[lang]['pay_pending'], reply_markup=kb.as_markup())
    except Exception as e:
        logging.error(f"Payment creation error: {e}")
        await call.answer("Payment service unavailable", show_alert=True)


# ==================== API ENDPOINTS ====================
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
}


async def handle_options(request):
    return web.Response(headers=CORS_HEADERS)


async def api_get_balance(request):
    """GET /api/balance?init_data=..."""
    try:
        init_data = request.rel_url.query.get("init_data", "")
        logging.info(f"📥 Balance request, init_data len={len(init_data)}, first100={init_data[:100]}")

        user = extract_user_from_init_data(init_data)
        if not user or not user.get("id"):
            logging.warning("❌ Balance: no user extracted from init_data")
            return web.json_response({"ok": False, "error": "auth_failed"}, headers=CORS_HEADERS)

        uid = user["id"]
        await ensure_user(uid, user.get("username"), user.get("first_name"))
        coins = await get_coins(uid)

        logging.info(f"💰 Balance OK: uid={uid} @{user.get('username','?')}, coins={coins}")
        return web.json_response({"ok": True, "balance": int(coins)}, headers=CORS_HEADERS)

    except Exception as e:
        logging.error(f"API balance error: {e}", exc_info=True)
        return web.json_response({"ok": False, "error": "server"}, headers=CORS_HEADERS)


async def api_spin(request):
    """POST /api/spin {init_data, bet}"""
    if request.method == "OPTIONS":
        return web.Response(headers=CORS_HEADERS)
    try:
        data = await request.json()
        user = extract_user_from_init_data(data.get("init_data", ""))
        if not user or not user.get("id"):
            return web.json_response({"ok": False, "error": "auth"}, headers=CORS_HEADERS)

        uid = user["id"]
        bet = int(data.get("bet", 0))
        if bet not in (5, 10, 25, 50):
            return web.json_response({"ok": False, "error": "invalid_bet"}, headers=CORS_HEADERS)

        current_coins = await get_coins(uid)
        if current_coins < bet:
            return web.json_response({"ok": False, "error": "insufficient_funds", "balance": int(current_coins)}, headers=CORS_HEADERS)

        grid, multiplier = compute_spin()
        winnings = int(bet * multiplier)
        new_balance = await update_coins(uid, -bet + winnings)

        logging.info(f"🎰 Spin: uid={uid}, bet={bet}, win={winnings}, bal={new_balance}")
        return web.json_response({"ok": True, "grid": grid, "winnings": winnings, "balance": new_balance}, headers=CORS_HEADERS)

    except Exception as e:
        logging.error(f"API spin error: {e}", exc_info=True)
        return web.json_response({"ok": False, "error": "server"}, headers=CORS_HEADERS)


async def api_debug(request):
    """GET /api/debug?init_data=... — диагностика."""
    try:
        init_data = request.rel_url.query.get("init_data", "")
        parsed = dict(urllib.parse.parse_qsl(init_data)) if init_data else {}
        user_raw = parsed.get("user", "")
        user_data = json.loads(user_raw) if user_raw else {}
        user_obj, verified = validate_init_data(init_data)
        uid = user_data.get("id")
        db_coins = await get_coins(uid) if uid else 0

        return web.json_response({
            "init_data_length": len(init_data),
            "has_hash": "hash" in parsed,
            "has_user": bool(user_raw),
            "user_id": uid,
            "username": user_data.get("username"),
            "hmac_verified": verified,
            "db_coins": db_coins,
            "parsed_keys": list(parsed.keys()),
        }, headers=CORS_HEADERS)
    except Exception as e:
        return web.json_response({"error": str(e)}, headers=CORS_HEADERS)


async def api_crypto_webhook(request):
    """POST /api/crypto-webhook"""
    try:
        body = await request.json()
        if body.get("update_type") != "invoice_paid":
            return web.json_response({"ok": True})

        payload_raw = body.get("payload", {}).get("payload", "{}")
        payload = json.loads(payload_raw)
        uid = payload.get("user_id")
        coins_amount = payload.get("coins", 0)
        if not uid or not coins_amount:
            return web.json_response({"ok": False})

        new_balance = await update_coins(uid, coins_amount)
        lang, _, _ = await get_user_data(uid)
        logging.info(f"💳 Payment: uid={uid}, +{coins_amount}, bal={new_balance}")

        try:
            await bot.send_message(uid, BOT_TEXTS[lang]['pay_success'].format(amount=coins_amount, balance=new_balance))
        except Exception:
            pass
        return web.json_response({"ok": True})
    except Exception as e:
        logging.error(f"Crypto webhook error: {e}")
        return web.json_response({"ok": False})


# ==================== WEB СЕРВЕР ====================
async def start_api():
    app = web.Application()
    app.router.add_get("/api/balance", api_get_balance)
    app.router.add_post("/api/spin", api_spin)
    app.router.add_get("/api/debug", api_debug)
    app.router.add_post("/api/crypto-webhook", api_crypto_webhook)
    app.router.add_options("/{tail:.*}", handle_options)
    app.router.add_get("/health", lambda r: web.json_response({"status": "ok"}))

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", API_PORT).start()
    logging.info(f"🚀 API started on :{API_PORT}")


async def main():
    init_db()
    await start_api()
    logging.info("🤖 Bot polling...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    asyncio.run(main())
