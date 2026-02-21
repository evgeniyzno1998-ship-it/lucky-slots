import logging
import sqlite3
import asyncio
import time
import os
import sys
import aiohttp
from collections import defaultdict
from typing import Callable, Any, Awaitable

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, BaseMiddleware
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import texts

# ==================== НАСТРОЙКИ ====================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID_RAW = os.getenv("ADMIN_ID")
CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN")  # Токен от @CryptoBot

if not BOT_TOKEN:
    sys.exit("ERROR: BOT_TOKEN не задан в файле .env!")
if not ADMIN_ID_RAW:
    sys.exit("ERROR: ADMIN_ID не задан в файле .env!")
if not CRYPTO_TOKEN:
    sys.exit("ERROR: CRYPTO_TOKEN не задан в файле .env!")

try:
    ADMIN_ID = int(ADMIN_ID_RAW)
except ValueError:
    sys.exit("ERROR: ADMIN_ID должен быть числом!")

# ==================== ПАКЕТЫ ЖЕТОНОВ ====================
# Формат: "название": (жетонов, цена в USDT)
COIN_PACKAGES = {
    "pack_50":  ("50 żetonów",  50,  0.50),
    "pack_100": ("100 żetonów", 100, 0.90),
    "pack_500": ("500 żetonów", 500, 4.00),
}

# ==================== RATE LIMITING ====================

RATE_LIMIT_MESSAGES = 5
RATE_LIMIT_WINDOW = 10
RATE_LIMIT_CALLBACKS = 10
RATE_LIMIT_CALLBACK_WINDOW = 5
BAN_DURATION = 60

_message_timestamps: dict[int, list[float]] = defaultdict(list)
_callback_timestamps: dict[int, list[float]] = defaultdict(list)
_banned_until: dict[int, float] = {}

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            is_callback = False
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            is_callback = True
        else:
            return await handler(event, data)

        if user_id == ADMIN_ID:
            return await handler(event, data)

        now = time.monotonic()

        if user_id in _banned_until:
            if now < _banned_until[user_id]:
                remaining = int(_banned_until[user_id] - now)
                if isinstance(event, Message):
                    await event.answer(f"⛔ Zbyt wiele żądań. Spróbuj za {remaining} sek.")
                elif isinstance(event, CallbackQuery):
                    await event.answer(f"⛔ Zbyt szybko! Poczekaj {remaining} sek.", show_alert=True)
                return
            else:
                del _banned_until[user_id]

        if is_callback:
            timestamps = _callback_timestamps[user_id]
            limit = RATE_LIMIT_CALLBACKS
            window = RATE_LIMIT_CALLBACK_WINDOW
        else:
            timestamps = _message_timestamps[user_id]
            limit = RATE_LIMIT_MESSAGES
            window = RATE_LIMIT_WINDOW

        cutoff = now - window
        while timestamps and timestamps[0] < cutoff:
            timestamps.pop(0)

        if len(timestamps) >= limit:
            _banned_until[user_id] = now + BAN_DURATION
            if isinstance(event, Message):
                await event.answer(f"⛔ Wykryto spam! Zablokowano na {BAN_DURATION} sek.")
            elif isinstance(event, CallbackQuery):
                await event.answer(f"⛔ Za szybko! Zablokowano na {BAN_DURATION} sek.", show_alert=True)
            return

        timestamps.append(now)
        return await handler(event, data)

# ==================== CASINO ====================

CASINO_LINKS = {
    "slottica": "https://slottica.com/pl?ref=TVOY_PARTNER_ID",
    "magic365": "https://magic365.pl/pl?ref=TVOY_PARTNER_ID",
    "gransino": "https://gransino.com/pl?ref=TVOY_PARTNER_ID",
    "slottyway": "https://slottyway.com/pl?ref=TVOY_PARTNER_ID"
}

BONUSES = {
    "slottica": "🎁 Bonus powitalny: 100% do 2000 PLN + 50 darmowych spinów!",
    "magic365": "🔥 Magic365: 150% bonus od pierwszego depozytu + 100 FS!",
    "gransino": "🆕 Gransino: 50 darmowych spinów bez depozytu!",
    "slottyway": "💎 Slottyway: 200% bonus + 50 spinów na Book of Dead"
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
BOT_USERNAME: str | None = None

# ==================== БАЗА ДАННЫХ ====================

def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                phone TEXT,
                referred_by INTEGER,
                referrals_count INTEGER DEFAULT 0,
                coins INTEGER DEFAULT 0,
                joined_date TEXT,
                last_click TEXT
            )
        ''')
        # Таблица для хранения инвойсов (ожидающих оплату)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                pack_key TEXT NOT NULL,
                coins INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')

def get_user(user_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()

def create_user(user_id, username, first_name, referred_by=None):
    with sqlite3.connect('users.db') as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, referred_by, joined_date) VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, username, first_name, referred_by)
        )

def update_user_phone(user_id, phone):
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))

def update_user_login(user_id, username, first_name):
    with sqlite3.connect('users.db') as conn:
        conn.execute(
            "UPDATE users SET username = ?, first_name = ? WHERE user_id = ?",
            (username, first_name, user_id)
        )

def add_referral(referrer_id, new_user_id):
    with sqlite3.connect('users.db') as conn:
        conn.execute(
            "UPDATE users SET referrals_count = referrals_count + 1, coins = coins + 10 WHERE user_id = ?",
            (referrer_id,)
        )
        conn.execute(
            "UPDATE users SET referred_by = ? WHERE user_id = ?",
            (referrer_id, new_user_id)
        )

def get_user_stats(user_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT referrals_count, coins FROM users WHERE user_id = ?", (user_id,))
        result = cur.fetchone()
    return result if result else (0, 0)

def add_coins(user_id, amount):
    with sqlite3.connect('users.db') as conn:
        conn.execute(
            "UPDATE users SET coins = coins + ? WHERE user_id = ?",
            (amount, user_id)
        )

def save_invoice(invoice_id, user_id, pack_key, coins, amount):
    with sqlite3.connect('users.db') as conn:
        conn.execute(
            "INSERT OR IGNORE INTO invoices (invoice_id, user_id, pack_key, coins, amount) VALUES (?, ?, ?, ?, ?)",
            (invoice_id, user_id, pack_key, coins, amount)
        )

def get_invoice(invoice_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM invoices WHERE invoice_id = ?", (invoice_id,))
        return cur.fetchone()

def mark_invoice_paid(invoice_id):
    with sqlite3.connect('users.db') as conn:
        conn.execute(
            "UPDATE invoices SET status = 'paid' WHERE invoice_id = ?",
            (invoice_id,)
        )

def get_pending_invoices():
    """Возвращает все неоплаченные инвойсы не старше 1 часа."""
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT invoice_id, user_id, coins, pack_key
            FROM invoices
            WHERE status = 'pending'
            AND created_at > datetime('now', '-1 hour')
        """)
        return cur.fetchall()

def get_all_users_with_phones():
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, first_name, phone, joined_date, referrals_count, coins FROM users WHERE phone IS NOT NULL"
        )
        return cur.fetchall()

def get_top_referrers(limit=10):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, username, first_name, referrals_count, coins
            FROM users WHERE referrals_count > 0
            ORDER BY referrals_count DESC, coins DESC LIMIT ?
        """, (limit,))
        return cur.fetchall()

def update_last_click(user_id):
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET last_click = datetime('now') WHERE user_id = ?", (user_id,))

# ==================== CRYPTOBOT API ====================

CRYPTOBOT_API = "https://pay.crypt.bot/api"

async def create_invoice(amount: float, pack_key: str, user_id: int) -> dict | None:
    """Создаёт инвойс через CryptoBot и возвращает данные."""
    payload = {
        "asset": "USDT",
        "amount": str(amount),
        "description": f"Zakup żetonów — {COIN_PACKAGES[pack_key][0]}",
        "payload": f"{user_id}:{pack_key}",
        "expires_in": 3600
    }
    headers = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}
    # Таймаут: 8 секунд на соединение, 10 секунд на ответ
    timeout = aiohttp.ClientTimeout(connect=8, total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{CRYPTOBOT_API}/createInvoice",
                json=payload,
                headers=headers
            ) as resp:
                data = await resp.json()
                if data.get("ok"):
                    return data["result"]
                else:
                    logger.error(f"CryptoBot error: {data}")
                    return None
    except asyncio.TimeoutError:
        logger.error("CryptoBot timeout — сервер не ответил за 10 сек")
        return None
    except Exception as e:
        logger.error(f"CryptoBot request failed: {e}")
        return None


async def check_invoice(invoice_id: str) -> str | None:
    """Проверяет статус инвойса: 'active' | 'paid' | 'expired'"""
    headers = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}
    timeout = aiohttp.ClientTimeout(connect=5, total=8)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{CRYPTOBOT_API}/getInvoices",
                params={"invoice_ids": invoice_id},
                headers=headers
            ) as resp:
                data = await resp.json()
                if data.get("ok") and data["result"]["items"]:
                    return data["result"]["items"][0]["status"]
    except asyncio.TimeoutError:
        logger.error("CryptoBot check timeout")
    except Exception as e:
        logger.error(f"CryptoBot check failed: {e}")
    return None

# ==================== КЛАВИАТУРЫ ====================

def main_menu():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Graj teraz")],
            [KeyboardButton(
                text="🎰 Lucky Slots",
                web_app=types.WebAppInfo(url="https://evgeniyzno1998-ship-it.github.io/lucky-slots/?api=https://lucky-slots-production.up.railway.app&bot={BOT_USERNAME}")
            )],
            [KeyboardButton(text="🎁 Bonusy")],
            [KeyboardButton(text="👥 Poleć znajomego"), KeyboardButton(text="💰 Moje żetony")],
            [KeyboardButton(text="💳 Kup żetony")]
        ],
        resize_keyboard=True
    )
    return kb

def request_phone_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Udostępnij numer", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb

def casino_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="Slottica", callback_data="casino_slottica")
    builder.button(text="Magic365", callback_data="casino_magic365")
    builder.button(text="Gransino", callback_data="casino_gransino")
    builder.button(text="Slottyway", callback_data="casino_slottyway")
    builder.adjust(2)
    return builder.as_markup()

def back_button():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Powrót", callback_data="back_to_menu")
    return builder.as_markup()

def packages_keyboard():
    """Клавиатура выбора пакета жетонов."""
    builder = InlineKeyboardBuilder()
    for key, (label, coins, price) in COIN_PACKAGES.items():
        builder.button(
            text=f"{label} — {price} USDT",
            callback_data=f"buy_{key}"
        )
    builder.adjust(1)
    return builder.as_markup()

def pay_keyboard(pay_url: str, invoice_id: str):
    """Кнопка оплаты + кнопка проверки."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Zapłać kryptowalutą", url=pay_url)
    builder.button(text="✅ Sprawdź płatność", callback_data=f"check_{invoice_id}")
    builder.adjust(1)
    return builder.as_markup()

# ==================== ОБРАБОТЧИКИ ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "brak"
    first_name = message.from_user.first_name or "Użytkownik"

    referrer_id = None
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref"):
        try:
            referrer_id = int(args[1].replace("ref", ""))
            if referrer_id == user_id:
                referrer_id = None
        except ValueError:
            pass

     args = message.text.split()
    # ПРОВЕРКА НА ПЕРЕХОД ИЗ ИГРЫ
    if len(args) > 1 and args[1] == "deposit":
        await buy_coins_menu(message) # Сразу вызываем меню покупки
        return

    existing_user = get_user(user_id)

    if not existing_user:
        create_user(user_id, username, first_name, referrer_id)
        if referrer_id:
            referrer = get_user(referrer_id)
            if referrer:
                add_referral(referrer_id, user_id)
                try:
                    await bot.send_message(referrer_id, "🎉 Ktoś dołączył po Twoim linku! Masz +10 Żetonów Casino!")
                except Exception:
                    pass
    else:
        update_user_login(user_id, username, first_name)

    user = get_user(user_id)

    if user and user[3]:
        await message.answer(texts.WELCOME, reply_markup=main_menu(), parse_mode="Markdown")
    else:
        await message.answer(texts.PHONE_REQUEST, reply_markup=request_phone_keyboard(), parse_mode="Markdown")

@dp.message(lambda message: message.contact is not None)
async def handle_contact(message: Message):
    update_user_phone(message.from_user.id, message.contact.phone_number)
    await message.answer(texts.PHONE_THANKS, reply_markup=main_menu(), parse_mode="Markdown")

@dp.message(lambda m: m.web_app_data is not None)
async def handle_webapp_data(message: Message):
    """
    Этот хэндлер больше не списывает жетоны — всё управляется через HTTP API (/api/spin).
    Оставлен только для логирования на случай отладки.
    """
    import json
    try:
        data = json.loads(message.web_app_data.data)
        logger.info(f"WebApp data received (ignored, API handles balance): {data}")
    except Exception:
        pass


async def casino_menu(message: Message):
    await message.answer(texts.CASINO_CHOOSE, reply_markup=casino_inline())

@dp.message(lambda message: message.text == "🎁 Bonusy")
async def show_bonuses(message: Message):
    text = texts.BONUS_HEADER.format(
        slottica=BONUSES['slottica'], magic365=BONUSES['magic365'],
        gransino=BONUSES['gransino'], slottyway=BONUSES['slottyway']
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu())

@dp.message(lambda message: message.text == "👥 Poleć znajomego")
async def referral_link(message: Message):
    user_id = message.from_user.id
    referrals_count, coins = get_user_stats(user_id)
    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref{user_id}"
    await message.answer(
        texts.REFERRAL_TEXT.format(link=ref_link, count=referrals_count, coins=coins),
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.text == "💰 Moje żetony")
async def show_coins(message: Message):
    _, coins = get_user_stats(message.from_user.id)
    await message.answer(texts.COINS_BALANCE.format(coins=coins), parse_mode="Markdown")

# ==================== ПОКУПКА ЖЕТОНОВ ====================

@dp.message(lambda message: message.text == "💳 Kup żetony")
async def buy_coins_menu(message: Message):
    text = (
        "💳 *Kup żetony kryptowalutą*\n\n"
        "Wybierz pakiet:\n\n"
        "🥉 50 żetonów — 0.50 USDT\n"
        "🥈 100 żetonów — 0.90 USDT *(oszczędzasz 10%)*\n"
        "🥇 500 żetonów — 4.00 USDT *(oszczędzasz 20%)*\n\n"
        "Płatność przez CryptoBot — szybko i bezpiecznie."
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=packages_keyboard())

@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def buy_package(call: CallbackQuery):
    pack_key = call.data.replace("buy_", "")

    if pack_key not in COIN_PACKAGES:
        await call.answer("Nieznany pakiet.", show_alert=True)
        return

    label, coins, price = COIN_PACKAGES[pack_key]
    user_id = call.from_user.id

    await call.answer()
    await call.message.edit_text("⏳ Tworzę link do płatności...", reply_markup=None)

    invoice = await create_invoice(price, pack_key, user_id)

    if not invoice:
        await call.message.edit_text(
            "❌ Błąd połączenia z CryptoBot. Spróbuj za chwilę."
        )
        return

    invoice_id = str(invoice["invoice_id"])
    pay_url = invoice["pay_url"]

    save_invoice(invoice_id, user_id, pack_key, coins, price)

    try:
        await call.message.edit_text(
            f"💳 Zakup {label}\n\n"
            f"Kwota: {price} USDT\n"
            f"Numer zamówienia: {invoice_id}\n\n"
            f"1. Kliknij przycisk ponizej aby zaplacic\n"
            f"2. Po oplaceniu kliknij Sprawdz platnosc\n\n"
            f"Link wazny przez 1 godzine",
            reply_markup=pay_keyboard(pay_url, invoice_id)
        )
    except Exception as e:
        logger.error(f"edit_text failed: {e}")
        await bot.send_message(
            call.from_user.id,
            f"💳 Zakup {label}\n\n"
            f"Kwota: {price} USDT\n\n"
            f"Kliknij aby zaplacic:",
            reply_markup=pay_keyboard(pay_url, invoice_id)
        )

@dp.callback_query(lambda c: c.data.startswith("check_"))
async def check_payment(call: CallbackQuery):
    invoice_id = call.data.replace("check_", "")
    user_id = call.from_user.id

    await call.answer("🔍 Sprawdzam płatność...")

    # Сначала смотрим в локальную БД — вдруг уже обработано
    invoice = get_invoice(invoice_id)
    if not invoice:
        await call.message.edit_text("❌ Nie znaleziono zamówienia.")
        return

    db_status = invoice[5]  # колонка status
    if db_status == "paid":
        await call.message.edit_text("✅ Płatność już została zaksięgowana!")
        return

    # Проверяем статус у CryptoBot
    status = await check_invoice(invoice_id)

    if status == "paid":
        coins = invoice[3]  # колонка coins
        add_coins(user_id, coins)
        mark_invoice_paid(invoice_id)

        await call.message.edit_text(
            f"✅ *Płatność potwierdzona!*\n\n"
            f"Na Twoje konto dodano *{coins} żetonów* 🎰\n\n"
            f"Użyj ich aby odblokować ekskluzywne bonusy!",
            parse_mode="Markdown"
        )
        logger.info(f"User {user_id} paid invoice {invoice_id}, +{coins} coins")

    elif status == "expired":
        await call.message.edit_text(
            "⌛ Link do płatności wygasł. Wróć do menu i zamów ponownie.",
            reply_markup=None
        )
    else:
        # Ещё не оплачено
        await call.message.edit_reply_markup(
            reply_markup=pay_keyboard(
                invoice["pay_url"] if invoice else "#",
                invoice_id
            )
        )
        await call.answer("⏳ Płatność jeszcze nie dotarła. Spróbuj za chwilę.", show_alert=True)

# ==================== CASINO CALLBACKS ====================

@dp.callback_query(lambda c: c.data.startswith("casino_"))
async def casino_callback(call: CallbackQuery):
    casino_key = call.data.replace("casino_", "")
    if casino_key in CASINO_LINKS:
        update_last_click(call.from_user.id)
        await call.message.edit_text(
            texts.CASINO_INFO.format(
                name=casino_key.capitalize(),
                bonus=BONUSES[casino_key],
                link=CASINO_LINKS[casino_key]
            ),
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=back_button()
        )
    await call.answer()

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery):
    await call.message.edit_text(texts.CASINO_CHOOSE, reply_markup=casino_inline())
    await call.answer()

# ==================== СЛОТЫ ====================

import random

# Символы и их веса (чем меньше вес — тем реже выпадает)
SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
WEIGHTS = [30, 25, 20, 15, 7, 3]  # сумма = 100

# Таблица выплат (множитель ставки при трёх одинаковых)
PAYOUTS = {
    "🍒": 2,   # x2
    "🍋": 3,   # x3
    "🍊": 4,   # x4
    "🍇": 6,   # x6
    "💎": 10,  # x10
    "7️⃣": 20,  # x20
}

# Выплата за два одинаковых (любых)
PAYOUT_TWO = 1  # возврат ставки

# Перевес казино ~7% достигается через веса символов

def spin_reels() -> list[str]:
    return random.choices(SYMBOLS, weights=WEIGHTS, k=3)

def calc_payout(reels: list[str], bet: int) -> tuple[int, str]:
    """Возвращает (выигрыш в жетонах, описание результата)."""
    a, b, c = reels
    if a == b == c:
        mult = PAYOUTS[a]
        return bet * mult, f"🎉 TRZY {a}! x{mult}!"
    elif a == b or b == c or a == c:
        return bet * PAYOUT_TWO, "✨ Para! Zwrot stawki."
    else:
        return 0, "😔 Brak wygranej."

def slots_bet_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="5 żetonów",  callback_data="slots_5")
    builder.button(text="10 żetonów", callback_data="slots_10")
    builder.button(text="25 żetonów", callback_data="slots_25")
    builder.button(text="🔙 Menu",    callback_data="slots_back")
    builder.adjust(3, 1)
    return builder.as_markup()

def slots_again_keyboard(bet: int):
    builder = InlineKeyboardBuilder()
    builder.button(text=f"🔄 Zagraj znowu ({bet} żet.)", callback_data=f"slots_{bet}")
    builder.button(text="💰 Zmień stawkę", callback_data="slots_menu")
    builder.button(text="🔙 Menu",         callback_data="slots_back")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(lambda m: m.text == "🎰 Jednoreki bandyta")
async def slots_menu(message: Message):
    _, coins = get_user_stats(message.from_user.id)
    await message.answer(
        f"🎰 *Jednoreki Bandyta*\n\n"
        f"Twój balans: *{coins} żetonów*\n\n"
        f"Wybierz stawkę:\n"
        f"• 5 żetonów → wygraj do x20\n"
        f"• 10 żetonów → wygraj do x20\n"
        f"• 25 żetonów → wygraj do x20\n\n"
        f"_Para = zwrot stawki. Trzy takie same = wygrana!_",
        parse_mode="Markdown",
        reply_markup=slots_bet_keyboard()
    )

@dp.callback_query(lambda c: c.data == "slots_menu")
async def slots_menu_cb(call: CallbackQuery):
    _, coins = get_user_stats(call.from_user.id)
    await call.message.edit_text(
        f"🎰 *Jednoreki Bandyta*\n\n"
        f"Twój balans: *{coins} żetonów*\n\n"
        f"Wybierz stawkę:",
        parse_mode="Markdown",
        reply_markup=slots_bet_keyboard()
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("slots_") and c.data[6:].isdigit())
async def slots_spin(call: CallbackQuery):
    bet = int(call.data.replace("slots_", ""))
    user_id = call.from_user.id

    _, coins = get_user_stats(user_id)

    if coins < bet:
        await call.answer(
            f"Niewystarczające żetony! Masz {coins}, potrzebujesz {bet}.",
            show_alert=True
        )
        return

    await call.answer()

    # Списываем ставку сразу
    with sqlite3.connect('users.db') as conn:
        conn.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (bet, user_id))

    # Анимация вращения
    spin_frames = [
        "🎰 Kręcę...\n\n❓ ❓ ❓",
        f"🎰 Kręcę...\n\n{random.choice(SYMBOLS)} ❓ ❓",
        f"🎰 Kręcę...\n\n{random.choice(SYMBOLS)} {random.choice(SYMBOLS)} ❓",
    ]

    msg = await call.message.edit_text(spin_frames[0])
    for frame in spin_frames[1:]:
        await asyncio.sleep(0.6)
        try:
            await msg.edit_text(frame)
        except Exception:
            pass

    # Результат
    reels = spin_reels()
    winnings, result_text = calc_payout(reels, bet)

    if winnings > 0:
        with sqlite3.connect('users.db') as conn:
            conn.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (winnings, user_id))

    _, new_coins = get_user_stats(user_id)
    net = winnings - bet

    result_line = f"+{net} żetonów" if net > 0 else (f"{net} żetonów" if net < 0 else "±0 żetonów")

    await asyncio.sleep(0.6)
    try:
        await msg.edit_text(
            f"🎰  {reels[0]}  {reels[1]}  {reels[2]}\n\n"
            f"{result_text}\n\n"
            f"Stawka: {bet} żet. → {result_line}\n"
            f"Balans: *{new_coins} żetonów*",
            parse_mode="Markdown",
            reply_markup=slots_again_keyboard(bet)
        )
    except Exception:
        pass

    logger.info(f"Slots: user={user_id} bet={bet} reels={reels} win={winnings}")

@dp.callback_query(lambda c: c.data == "slots_back")
async def slots_back(call: CallbackQuery):
    await call.message.delete()
    await call.answer()

# ==================== АДМИНКА ====================

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer(texts.ADMIN_DENIED)
        return

    top_refs = get_top_referrers()
    users = get_all_users_with_phones()

    if not users and not top_refs:
        await message.answer(texts.ADMIN_NO_USERS)
        return

    text = ""
    if top_refs:
        text += texts.ADMIN_TOP
        for i, ref in enumerate(top_refs, 1):
            text += texts.ADMIN_TOP_LINE.format(
                place=i, name=ref[2], username=ref[1] or "brak",
                count=ref[3], coins=ref[4]
            )
        text += "\n"

    if users:
        text += texts.ADMIN_HEADER
        for user in users:
            text += texts.ADMIN_LINE.format(
                name=user[2], username=user[1] or "brak",
                user_id=user[0], phone=user[3],
                date=user[4], coins=user[6], referrals=user[5]
            )

    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            await message.answer(text[i:i+4000], parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

@dp.message(Command("stats"))
async def stats_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Brak dostępu.")
        return

    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()

        # Всего пользователей
        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        # Всего инвойсов
        cur.execute("SELECT COUNT(*) FROM invoices")
        total_invoices = cur.fetchone()[0]

        # Оплаченных
        cur.execute("SELECT COUNT(*) FROM invoices WHERE status = 'paid'")
        paid_invoices = cur.fetchone()[0]

        # Ожидают оплаты
        cur.execute("SELECT COUNT(*) FROM invoices WHERE status = 'pending'")
        pending_invoices = cur.fetchone()[0]

        # Общая сумма
        cur.execute("SELECT SUM(amount) FROM invoices WHERE status = 'paid'")
        total_revenue = cur.fetchone()[0] or 0

        # Статистика по пакетам
        cur.execute("""
            SELECT pack_key, COUNT(*) as cnt, SUM(amount) as revenue
            FROM invoices WHERE status = 'paid'
            GROUP BY pack_key ORDER BY cnt DESC
        """)
        pack_stats = cur.fetchall()

        # Последние 5 оплат с данными пользователя
        cur.execute("""
            SELECT i.invoice_id, i.user_id, u.username, u.first_name,
                   i.pack_key, i.coins, i.amount, i.created_at
            FROM invoices i
            LEFT JOIN users u ON i.user_id = u.user_id
            WHERE i.status = 'paid'
            ORDER BY i.created_at DESC
            LIMIT 5
        """)
        last_payments = cur.fetchall()

    # Конверсия
    conversion = round(paid_invoices / total_invoices * 100, 1) if total_invoices > 0 else 0

    text = (
        "📊 *Statystyki płatności*\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"👥 Użytkownicy: *{total_users}*\n"
        f"📋 Wszystkich zamówień: *{total_invoices}*\n"
        f"✅ Opłaconych: *{paid_invoices}*\n"
        f"⏳ Oczekujących: *{pending_invoices}*\n"
        f"📈 Konwersja: *{conversion}%*\n"
        f"💰 Przychód: *${total_revenue:.2f} USDT*\n\n"
    )

    if pack_stats:
        text += "🎁 *Sprzedaż wg pakietu:*\n"
        for pack_key, cnt, revenue in pack_stats:
            label = COIN_PACKAGES.get(pack_key, (pack_key,))[0]
            text += f"  • {label}: {cnt} szt. / ${revenue:.2f}\n"
        text += "\n"

    if last_payments:
        text += "🕒 *Ostatnie płatności:*\n"
        for inv_id, uid, username, fname, pack_key, coins, amount, date in last_payments:
            uname = f"@{username}" if username and username != "brak" else fname or str(uid)
            label = COIN_PACKAGES.get(pack_key, (pack_key,))[0]
            date_short = date[:16] if date else "—"
            text += f"  • {uname} — {label} (${amount}) [{date_short}]\n"

    await message.answer(text, parse_mode="Markdown")

# ==================== ФОНОВАЯ ПРОВЕРКА ОПЛАТ ====================

async def payment_checker():
    """
    Каждые 10 секунд проверяет все pending инвойсы:
    - Оплачен → зачисляет жетоны + уведомляет пользователя
    - Не оплачен → молчит
    - Прошло 30 минут без оплаты → просит повторить заказ
    """
    logger.info("Payment checker started (interval: 10s)")
    while True:
        await asyncio.sleep(10)

        # Pending инвойсы младше 30 минут — ещё ждём
        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT invoice_id, user_id, coins, pack_key
                FROM invoices
                WHERE status = 'pending'
                AND created_at > datetime('now', '-30 minutes')
            """)
            pending = cur.fetchall()

        # Инвойсы старше 30 минут — напоминаем и закрываем
        with sqlite3.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT invoice_id, user_id, pack_key
                FROM invoices
                WHERE status = 'pending'
                AND created_at <= datetime('now', '-30 minutes')
            """)
            expired_pending = cur.fetchall()

        # Обрабатываем истёкшие без оплаты
        for invoice_id, user_id, pack_key in expired_pending:
            try:
                label = COIN_PACKAGES.get(pack_key, ("żetony",))[0]
                with sqlite3.connect('users.db') as conn:
                    conn.execute(
                        "UPDATE invoices SET status = 'expired' WHERE invoice_id = ?",
                        (invoice_id,)
                    )
                await bot.send_message(
                    user_id,
                    f"⏰ Twój link do płatności za {label} wygasł.\n\n"
                    f"Jeśli chcesz kupić żetony — wróć do menu i złóż zamówienie ponownie 👇",
                    reply_markup=main_menu()
                )
                logger.info(f"Invoice {invoice_id} expired (30min), notified user {user_id}")
            except Exception as e:
                logger.error(f"Expiry notify error for {invoice_id}: {e}")

        # Обрабатываем активные инвойсы
        for invoice_id, user_id, coins, pack_key in pending:
            try:
                status = await check_invoice(invoice_id)

                if status == "paid":
                    add_coins(user_id, coins)
                    mark_invoice_paid(invoice_id)
                    label = COIN_PACKAGES.get(pack_key, ("żetony",))[0]
                    logger.info(f"Auto-credited {coins} coins to user {user_id} (invoice {invoice_id})")
                    await bot.send_message(
                        user_id,
                        f"✅ Płatność potwierdzona!\n\n"
                        f"Na Twoje konto dodano {coins} żetonów ({label}) 🎰\n\n"
                        f"Użyj ich aby odblokować ekskluzywne bonusy!",
                        reply_markup=main_menu()
                    )

                elif status == "expired":
                    with sqlite3.connect('users.db') as conn:
                        conn.execute(
                            "UPDATE invoices SET status = 'expired' WHERE invoice_id = ?",
                            (invoice_id,)
                        )
                # status == "active" → молчим, ждём следующей проверки

            except Exception as e:
                logger.error(f"Checker error for invoice {invoice_id}: {e}")

# ==================== API ДЛЯ MINI APP ====================
# Mini App обращается к боту через HTTP API для получения баланса и записи спинов.
# Верификация через Telegram initData — подделать нельзя.

import hashlib
import hmac
import urllib.parse
from aiohttp import web

API_PORT = int(os.getenv("PORT", 8081))

def verify_telegram_init_data(init_data: str) -> dict | None:
    """
    Проверяет подлинность данных от Telegram Mini App.
    Возвращает dict с данными пользователя или None если подделка.
    """
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed.pop("hash", None)
        if not received_hash:
            return None

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed.items())
        )
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()  # type: ignore

        if not hmac.compare_digest(expected_hash, received_hash):
            return None

        import json
        user_data = json.loads(parsed.get("user", "{}"))
        return user_data
    except Exception as e:
        logger.error(f"initData verify error: {e}")
        return None

async def api_get_balance(request: web.Request) -> web.Response:
    """GET /api/balance?init_data=... → возвращает баланс пользователя."""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, ngrok-skip-browser-warning",
    }
    init_data = request.rel_url.query.get("init_data", "")
    user = verify_telegram_init_data(init_data)

    if not user:
        return web.json_response({"ok": False, "error": "Unauthorized"}, status=401, headers=headers)

    user_id = user.get("id")
    _, coins = get_user_stats(user_id)
    return web.json_response({"ok": True, "balance": coins, "user_id": user_id}, headers=headers)

async def api_spin(request: web.Request) -> web.Response:
    """POST /api/spin → списывает ставку, возвращает результат, обновляет баланс."""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, ngrok-skip-browser-warning",
    }

    if request.method == "OPTIONS":
        return web.Response(status=200, headers=headers)

    try:
        import json as _json
        body = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "Bad JSON"}, status=400, headers=headers)

    init_data = body.get("init_data", "")
    user = verify_telegram_init_data(init_data)

    if not user:
        return web.json_response({"ok": False, "error": "Unauthorized"}, status=401, headers=headers)

    user_id = int(user.get("id"))
    bet = int(body.get("bet", 0))

    if bet <= 0:
        return web.json_response({"ok": False, "error": "Invalid bet"}, status=400, headers=headers)

    # Атомарно проверяем и списываем баланс
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return web.json_response({"ok": False, "error": "User not found"}, status=404, headers=headers)
        current_coins = row[0]
        if current_coins < bet:
            return web.json_response({
                "ok": False,
                "error": "Insufficient balance",
                "balance": current_coins
            }, status=400, headers=headers)
        # Списываем
        conn.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (bet, user_id))

    # Результат спина считается на стороне игры — бот просто записывает
    winnings = int(body.get("winnings", 0))
    reels    = body.get("reels", [])
    net      = winnings - bet

    if winnings > 0:
        with sqlite3.connect('users.db') as conn:
            conn.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (winnings, user_id))

    _, new_balance = get_user_stats(user_id)
    logger.info(f"API spin: user={user_id} bet={bet} win={winnings} balance={new_balance}")

    return web.json_response({
        "ok": True,
        "balance": new_balance,
        "net": net,
        "winnings": winnings
    }, headers=headers)

async def api_options(request: web.Request) -> web.Response:
    """OPTIONS preflight для CORS."""
    return web.Response(status=200, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, ngrok-skip-browser-warning",
    })

async def start_api_server():
    """Запускает HTTP API сервер на порту API_PORT."""
    app = web.Application()
    app.router.add_get("/api/balance", api_get_balance)
    app.router.add_post("/api/spin", api_spin)
    app.router.add_options("/api/spin", api_options)
    app.router.add_options("/api/balance", api_options)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", API_PORT)
    await site.start()
    logger.info(f"API server started on port {API_PORT}")

# ==================== ЗАПУСК ====================

async def main():
    global BOT_USERNAME
    init_db()
    bot_info = await bot.get_me()
    BOT_USERNAME = bot_info.username
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    asyncio.create_task(payment_checker())
    asyncio.create_task(start_api_server())

    print(f"✅ Бот @{BOT_USERNAME} запущен! API на порту {API_PORT}. Нажми Ctrl+C для остановки.")
    await dp.start_polling(bot)

if __name__ == '__main__':

    asyncio.run(main())



