import logging, sqlite3, asyncio, os, json, urllib.parse, hashlib, hmac, random, time, math
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# ==================== CONFIG ====================
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN")
API_PORT = int(os.getenv("PORT", 8080))
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://lucky-slots-production.up.railway.app")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://evgeniyzno1998-ship-it.github.io/lucky-slots/")
REFERRAL_BONUS = 10

# ==================== DUAL BALANCE & CURRENCY ====================
# USDT balance is stored as cents (integer) for precision: 500 = $5.00
# Stars balance is separate, stored as integer count
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

# ==================== LOCALIZATION ====================
LANGUAGES = {'pl': '🇵🇱 Polski', 'ua': '🇺🇦 Українська', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
BOT_TEXTS = {
    'pl': {'welcome': 'Witaj w Lucky Slots! 🎰\nKliknij przycisk poniżej aby zagrać!', 'play': '🎰 Graj teraz', 'buy': '💳 Kup żetony', 'set': '⚙️ Język', 'bal': '💰 Moje żetony', 'ref': '👥 Poleć znajomego', 'balance_text': '💰 Twój balans: {c} żetonów', 'lang_ok': '✅ Język zmieniony!', 'token': 'żetonów', 'buy_m': '💳 Wybierz pakiet:', 'ref_t': '👥 <b>Twój link:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Zaprosiłeś: <b>{refs}</b>\n💰 Zdobyłeś: <b>{earned}</b> żetonów\n\n💡 Za każdego: <b>{bonus}</b> żetonów!', 'ref_welcome': '🎉 Bonus {bonus} żetonów!', 'ref_earned': '🎉 +{bonus} żetonów za polecenie!', 'pay_success': '✅ +{amount} żetonów!\nBalans: {balance}', 'pay_pending': '⏳ Kliknij aby zapłacić:'},
    'ua': {'welcome': 'Вітаємо у Lucky Slots! 🎰\nНатисніть кнопку щоб грати!', 'play': '🎰 Грати', 'buy': '💳 Купити жетони', 'set': '⚙️ Мова', 'bal': '💰 Баланс', 'ref': '👥 Друзі', 'balance_text': '💰 Баланс: {c} жетонів', 'lang_ok': '✅ Мову змінено!', 'token': 'жетонів', 'buy_m': '💳 Оберіть пакет:', 'ref_t': '👥 <b>Посилання:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Запросили: <b>{refs}</b>\n💰 Зароблено: <b>{earned}</b>\n\n💡 За кожного: <b>{bonus}</b>!', 'ref_welcome': '🎉 Бонус {bonus} жетонів!', 'ref_earned': '🎉 +{bonus} жетонів!', 'pay_success': '✅ +{amount} жетонів!\nБаланс: {balance}', 'pay_pending': '⏳ Натисніть для оплати:'},
    'ru': {'welcome': 'Добро пожаловать! 🎰\nНажмите кнопку чтобы играть!', 'play': '🎰 Играть', 'buy': '💳 Купить жетоны', 'set': '⚙️ Язык', 'bal': '💰 Баланс', 'ref': '👥 Друзья', 'balance_text': '💰 Баланс: {c} жетонов', 'lang_ok': '✅ Язык изменен!', 'token': 'жетонов', 'buy_m': '💳 Выберите пакет:', 'ref_t': '👥 <b>Ссылка:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Приглашено: <b>{refs}</b>\n💰 Заработано: <b>{earned}</b>\n\n💡 За каждого: <b>{bonus}</b>!', 'ref_welcome': '🎉 Бонус {bonus} жетонов!', 'ref_earned': '🎉 +{bonus} жетонов!', 'pay_success': '✅ +{amount} жетонов!\nБаланс: {balance}', 'pay_pending': '⏳ Нажмите для оплаты:'},
    'en': {'welcome': 'Welcome to Lucky Slots! 🎰\nTap the button to play!', 'play': '🎰 Play', 'buy': '💳 Buy Coins', 'set': '⚙️ Language', 'bal': '💰 Balance', 'ref': '👥 Friends', 'balance_text': '💰 Balance: {c} coins', 'lang_ok': '✅ Language changed!', 'token': 'coins', 'buy_m': '💳 Choose package:', 'ref_t': '👥 <b>Link:</b>\n<code>https://t.me/{b}?start=ref{u}</code>\n\n📊 Invited: <b>{refs}</b>\n💰 Earned: <b>{earned}</b>\n\n💡 Per friend: <b>{bonus}</b>!', 'ref_welcome': '🎉 Bonus {bonus} coins!', 'ref_earned': '🎉 +{bonus} coins!', 'pay_success': '✅ +{amount} coins!\nBalance: {balance}', 'pay_pending': '⏳ Click to pay:'},
}
PACKAGES = {"50": 0.50, "100": 0.90, "500": 4.00}

# ==================== SYMBOLS ====================
BASE_SYMS = ['🍒', '🍋', '🍊', '🍇', '🍫', '🍭', '🍬', '💎']
BONUS_SYMS = ['👑', '💎', '⭐', '❤️', '🍀', '🧲', '💰', '🌈']
SCATTER = '🎰'; BOMB = '💣'
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

# ==================== DATABASE ====================
DB_PATH = 'users.db'
_db_lock = asyncio.Lock()

def _conn():
    c = sqlite3.connect(DB_PATH); c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA busy_timeout=5000"); c.execute("PRAGMA synchronous=NORMAL"); c.row_factory = sqlite3.Row; return c

def init_db():
    with _conn() as c:
        # === USERS — основная таблица клиентов ===
        c.execute('''CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            tg_language_code TEXT,
            is_premium INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 0,
            free_spins INTEGER DEFAULT 0,
            total_wagered INTEGER DEFAULT 0,
            total_won INTEGER DEFAULT 0,
            total_spins INTEGER DEFAULT 0,
            biggest_win INTEGER DEFAULT 0,
            total_deposited_usd REAL DEFAULT 0,
            total_withdrawn_usd REAL DEFAULT 0,
            referrals_count INTEGER DEFAULT 0,
            referred_by INTEGER DEFAULT NULL,
            language TEXT DEFAULT 'pl',
            last_wheel TEXT DEFAULT '',
            last_game TEXT DEFAULT '',
            last_login TEXT DEFAULT '',
            last_bot_interaction TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        # Migration: add new columns to existing DB
        new_cols = [
            ("free_spins","INTEGER DEFAULT 0"),("total_wagered","INTEGER DEFAULT 0"),
            ("total_won","INTEGER DEFAULT 0"),("total_spins","INTEGER DEFAULT 0"),
            ("biggest_win","INTEGER DEFAULT 0"),("last_wheel","TEXT DEFAULT ''"),
            ("created_at","TEXT DEFAULT CURRENT_TIMESTAMP"),("language","TEXT DEFAULT 'pl'"),
            ("referred_by","INTEGER DEFAULT NULL"),("last_name","TEXT"),
            ("tg_language_code","TEXT"),("is_premium","INTEGER DEFAULT 0"),
            ("last_game","TEXT DEFAULT ''"),("last_login","TEXT DEFAULT ''"),
            ("last_bot_interaction","TEXT DEFAULT ''"),
            ("total_deposited_usd","REAL DEFAULT 0"),("total_withdrawn_usd","REAL DEFAULT 0"),
            # NEW: dual balance system
            ("balance_usdt_cents","INTEGER DEFAULT 0"),  # USDT balance in cents (500 = $5.00)
            ("balance_stars","INTEGER DEFAULT 0"),        # Telegram Stars balance
            ("display_currency","TEXT DEFAULT 'USD'"),    # preferred display currency
            ("total_wagered_usdt_cents","INTEGER DEFAULT 0"),
            ("total_won_usdt_cents","INTEGER DEFAULT 0"),
            ("total_wagered_stars","INTEGER DEFAULT 0"),
            ("total_won_stars","INTEGER DEFAULT 0"),
        ]
        for col, d in new_cols:
            try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {d}")
            except: pass

        # === BET_HISTORY — история каждой ставки ===
        c.execute('''CREATE TABLE IF NOT EXISTS bet_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            game TEXT NOT NULL,
            bet_type TEXT NOT NULL,
            bet_amount INTEGER NOT NULL,
            win_amount INTEGER NOT NULL,
            profit INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            multiplier REAL DEFAULT 0,
            is_bonus INTEGER DEFAULT 0,
            is_free_spin INTEGER DEFAULT 0,
            details TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')

        # === PAYMENTS — история платежей in/out ===
        c.execute('''CREATE TABLE IF NOT EXISTS payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            direction TEXT NOT NULL,
            amount_usd REAL NOT NULL,
            amount_coins INTEGER NOT NULL,
            method TEXT DEFAULT 'crypto_bot',
            status TEXT DEFAULT 'completed',
            invoice_id TEXT DEFAULT '',
            balance_before INTEGER DEFAULT 0,
            balance_after INTEGER DEFAULT 0,
            details TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')

        # === INDEXES for fast queries ===
        c.execute("CREATE INDEX IF NOT EXISTS idx_bets_user ON bet_history(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_bets_created ON bet_history(created_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_bets_game ON bet_history(game)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_payments_created ON payments(created_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_users_created ON users(created_at)")

async def db(q, p=(), fetch=False, one=False):
    async with _db_lock:
        def r():
            with _conn() as c:
                cur = c.execute(q, p)
                if one: return cur.fetchone()
                if fetch: return cur.fetchall()
        return await asyncio.get_event_loop().run_in_executor(None, r)

def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")

async def ensure_user(uid, un=None, fn=None, ln=None, lang_code=None, is_prem=False):
    """Создаёт или обновляет пользователя. Сохраняет все TG данные."""
    e = await db("SELECT user_id FROM users WHERE user_id=?", (int(uid),), one=True)
    if not e:
        await db(
            "INSERT OR IGNORE INTO users(user_id,username,first_name,last_name,tg_language_code,is_premium,created_at,last_bot_interaction) VALUES(?,?,?,?,?,?,?,?)",
            (int(uid), un, fn, ln, lang_code, 1 if is_prem else 0, _now(), _now())
        )
        return True
    else:
        await db(
            "UPDATE users SET username=COALESCE(?,username),first_name=COALESCE(?,first_name),last_name=COALESCE(?,last_name),tg_language_code=COALESCE(?,tg_language_code),is_premium=?,last_bot_interaction=? WHERE user_id=?",
            (un, fn, ln, lang_code, 1 if is_prem else 0, _now(), int(uid))
        )
    return False

async def update_last_login(uid):
    """Обновляет last_login при каждом входе в миниапп."""
    await db("UPDATE users SET last_login=? WHERE user_id=?", (_now(), int(uid)))

async def update_last_game(uid, game_name):
    """Обновляет последнюю игру в которую играл."""
    await db("UPDATE users SET last_game=? WHERE user_id=?", (game_name, int(uid)))

async def get_user(uid):
    return await db("SELECT * FROM users WHERE user_id=?", (int(uid),), one=True)

async def add_coins(uid, delta):
    await db("UPDATE users SET coins=MAX(0,coins+?) WHERE user_id=?", (delta, int(uid)))
    r = await db("SELECT coins FROM users WHERE user_id=?", (int(uid),), one=True)
    return r['coins'] if r else 0

async def add_usdt(uid, delta_cents):
    """Add/subtract USDT balance in cents. delta_cents can be negative."""
    await db("UPDATE users SET balance_usdt_cents=MAX(0,balance_usdt_cents+?) WHERE user_id=?", (int(delta_cents), int(uid)))
    r = await db("SELECT balance_usdt_cents FROM users WHERE user_id=?", (int(uid),), one=True)
    return r['balance_usdt_cents'] if r else 0

async def add_stars(uid, delta):
    """Add/subtract Stars balance."""
    await db("UPDATE users SET balance_stars=MAX(0,balance_stars+?) WHERE user_id=?", (int(delta), int(uid)))
    r = await db("SELECT balance_stars FROM users WHERE user_id=?", (int(uid),), one=True)
    return r['balance_stars'] if r else 0

def usdt_cents_to_display(cents, currency='USD'):
    """Convert USDT cents to display currency amount."""
    usd = cents / 100.0
    rate = CURRENCY_RATES.get(currency, 1.0)
    return round(usd * rate, 2)

def display_to_usdt_cents(amount, currency='USD'):
    """Convert display currency amount to USDT cents."""
    rate = CURRENCY_RATES.get(currency, 1.0)
    usd = amount / rate
    return int(round(usd * 100))

async def record_bet(uid, game, bet_type, bet_amt, win_amt, balance_after, multiplier=0, is_bonus=False, is_free=False, details=""):
    """Записывает КАЖДУЮ ставку в историю."""
    profit = win_amt - bet_amt
    await db(
        "INSERT INTO bet_history(user_id,game,bet_type,bet_amount,win_amount,profit,balance_after,multiplier,is_bonus,is_free_spin,details,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (int(uid), game, bet_type, bet_amt, win_amt, profit, balance_after, multiplier, 1 if is_bonus else 0, 1 if is_free else 0, details, _now())
    )
    # Обновляем агрегаты в users
    await db(
        "UPDATE users SET total_spins=total_spins+1,total_wagered=total_wagered+?,total_won=total_won+?,biggest_win=MAX(biggest_win,?) WHERE user_id=?",
        (bet_amt, win_amt, win_amt, int(uid))
    )

async def record_payment(uid, direction, amount_usd, amount_coins, method="crypto_bot", status="completed", invoice_id="", details=""):
    """Записывает КАЖДЫЙ платёж (deposit/withdrawal)."""
    u = await get_user(uid)
    bal_before = u['coins'] if u else 0
    bal_after = bal_before + amount_coins if direction == "deposit" else bal_before - amount_coins
    await db(
        "INSERT INTO payments(user_id,direction,amount_usd,amount_coins,method,status,invoice_id,balance_before,balance_after,details,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (int(uid), direction, amount_usd, amount_coins, method, status, invoice_id, bal_before, bal_after, details, _now())
    )
    # Обновляем total_deposited/withdrawn в users
    if direction == "deposit":
        await db("UPDATE users SET total_deposited_usd=total_deposited_usd+? WHERE user_id=?", (amount_usd, int(uid)))
    else:
        await db("UPDATE users SET total_withdrawn_usd=total_withdrawn_usd+? WHERE user_id=?", (amount_usd, int(uid)))

# ==================== AUTH ====================
def mktok(uid): return hmac.new(BOT_TOKEN.encode(), str(uid).encode(), hashlib.sha256).hexdigest()[:32]

def get_uid(data=None, query=None):
    idata = ""; uid_p = tok_p = None
    if query: idata=query.get("init_data",""); uid_p=query.get("uid",""); tok_p=query.get("token","")
    if data: idata=data.get("init_data","") or idata; uid_p=data.get("uid","") or uid_p; tok_p=data.get("token","") or tok_p
    if idata:
        try:
            p=dict(urllib.parse.parse_qsl(idata)); u=p.get("user","")
            if u:
                uid=json.loads(u).get("id")
                if uid: return int(uid)
        except: pass
    if uid_p:
        try: return int(uid_p)
        except: pass
    return None

# ==================== GAME LOGIC ====================
def _bmult():
    t=sum(w for w,_ in BOMB_WEIGHTS); r=random.uniform(0,t); c=0
    for w,m in BOMB_WEIGHTS:
        c+=w
        if r<=c: return m
    return 2

def base_spin(bet):
    g=[]; sc=0
    for _ in range(30):
        if random.random()<0.05: g.append(SCATTER); sc+=1
        else: g.append(random.choice(BASE_SYMS))
    co={}
    for s in g:
        if s!=SCATTER: co[s]=co.get(s,0)+1
    m=0.0
    for _,cnt in co.items():
        if cnt>=12: m+=5.0
        elif cnt>=8: m+=1.5
    return {"grid":g,"winnings":int(bet*m),"scatter_count":sc,"triggered_bonus":sc>=4}

def bonus_spin(bet):
    g=[]; bombs=[]; sc=0
    for i in range(30):
        r=random.random()
        if r<0.03: g.append(SCATTER); sc+=1
        elif r<0.13: g.append(BOMB); bombs.append(i)
        else: g.append(random.choice(BONUS_SYMS))
    co={}
    for s in g:
        if s not in(SCATTER,BOMB): co[s]=co.get(s,0)+1
    m=0.0; ws={}
    for sym,cnt in co.items():
        if cnt>=12: m+=10.0; ws[sym]=cnt
        elif cnt>=10: m+=5.0; ws[sym]=cnt
        elif cnt>=8: m+=3.0; ws[sym]=cnt
        elif cnt>=6: m+=2.0; ws[sym]=cnt
    bw=int(bet*m); bl=[]; tbm=1
    for p in bombs:
        bm=_bmult(); bl.append({"pos":p,"mult":bm}); tbm*=bm
    fw=bw*tbm if bw>0 else 0
    rt=sc>=3
    return {"grid":g,"winnings":int(fw),"bombs":bl,"total_bomb_mult":tbm,"base_win":bw,"scatter_count":sc,"retrigger":rt,"extra_spins":5 if rt else 0,"winning_symbols":ws}

def full_bonus(bet):
    ts=10; d=0; res=[]; tw=0
    while d<ts:
        r=bonus_spin(bet); d+=1; tw+=r["winnings"]
        r.update({"spin_number":d,"total_spins":ts,"running_total":tw})
        res.append(r)
        if r["retrigger"]: ts=min(ts+r["extra_spins"],30)
    return {"spins":res,"total_win":tw,"total_spins_played":d}

def spin_wheel():
    t=sum(w for w,_,_ in WHEEL_PRIZES); r=random.uniform(0,t); c=0
    for w,pt,v in WHEEL_PRIZES:
        c+=w
        if r<=c: return {"type":pt,"value":v}
    return {"type":"coins","value":5}

def vip_level(wagered):
    lv=VIP_LEVELS[0]
    for l in VIP_LEVELS:
        if wagered>=l['min']: lv=l
    return lv

# ==================== KEYBOARDS ====================
def main_menu(uid, bname, lang):
    t=BOT_TEXTS[lang]; tok=mktok(uid)
    url=f"{WEBAPP_URL}?api={urllib.parse.quote(PUBLIC_URL,safe='')}&bot={bname}&lang={lang}&uid={uid}&token={tok}"
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t['play'], web_app=WebAppInfo(url=url))],
        [KeyboardButton(text=t['buy']), KeyboardButton(text=t['bal'])],
        [KeyboardButton(text=t['ref']), KeyboardButton(text=t['set'])]
    ], resize_keyboard=True)

def pkgs_kb(lang):
    t=BOT_TEXTS[lang]['token']; b=InlineKeyboardBuilder()
    for a,p in PACKAGES.items(): b.button(text=f"{a} {t} — {p} USDT", callback_data=f"buy_{a}")
    return b.adjust(1).as_markup()

# ==================== BOT HANDLERS ====================
bot = Bot(token=BOT_TOKEN); dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    uid=msg.from_user.id; args=msg.text.split()
    u = msg.from_user
    is_new=await ensure_user(uid, u.username, u.first_name, u.last_name, u.language_code, getattr(u, 'is_premium', False))
    bi=await bot.get_me(); usr=await get_user(uid); lang=usr['language'] if usr else 'pl'
    if len(args)>1 and args[1]=="deposit":
        await msg.answer(BOT_TEXTS[lang]['buy_m'], reply_markup=pkgs_kb(lang)); return
    if is_new and len(args)>1 and args[1].startswith("ref"):
        try:
            rid=int(args[1][3:])
            if rid!=uid:
                await db("UPDATE users SET referred_by=? WHERE user_id=? AND referred_by IS NULL",(rid,uid))
                await db("UPDATE users SET referrals_count=referrals_count+1,coins=coins+? WHERE user_id=?",(REFERRAL_BONUS,rid))
                await add_coins(uid,REFERRAL_BONUS)
                # Record referral bonus as payment for both
                await record_payment(uid, "deposit", 0, REFERRAL_BONUS, method="referral_bonus", details=f"referred_by={rid}")
                await record_payment(rid, "deposit", 0, REFERRAL_BONUS, method="referral_bonus", details=f"new_referral={uid}")
                ru=await get_user(rid); rl=ru['language'] if ru else 'pl'
                try: await bot.send_message(rid, BOT_TEXTS[rl]['ref_earned'].format(bonus=REFERRAL_BONUS))
                except: pass
                await msg.answer(BOT_TEXTS[lang]['ref_welcome'].format(bonus=REFERRAL_BONUS))
        except: pass
    await msg.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(uid, bi.username, lang))

@dp.message(F.text)
async def handle_btn(msg: Message):
    uid=msg.from_user.id; txt=msg.text.strip()
    fu = msg.from_user
    await ensure_user(uid, fu.username, fu.first_name, fu.last_name, fu.language_code, getattr(fu, 'is_premium', False))
    u=await get_user(uid); lang=u['language'] if u else 'pl'; bi=await bot.get_me()
    if any(txt==BOT_TEXTS[l]['buy'] for l in BOT_TEXTS): await msg.answer(BOT_TEXTS[lang]['buy_m'], reply_markup=pkgs_kb(lang))
    elif any(txt==BOT_TEXTS[l]['bal'] for l in BOT_TEXTS): await msg.answer(BOT_TEXTS[lang]['balance_text'].format(c=u['coins'] if u else 0))
    elif any(txt==BOT_TEXTS[l]['ref'] for l in BOT_TEXTS):
        refs=u['referrals_count'] if u else 0
        await msg.answer(BOT_TEXTS[lang]['ref_t'].format(b=bi.username,u=uid,refs=refs,earned=refs*REFERRAL_BONUS,bonus=REFERRAL_BONUS), parse_mode="HTML")
    elif any(txt==BOT_TEXTS[l]['set'] for l in BOT_TEXTS):
        kb=InlineKeyboardBuilder()
        for c,n in LANGUAGES.items(): kb.button(text=n, callback_data=f"sl_{c}")
        await msg.answer("🌐", reply_markup=kb.adjust(2).as_markup())

@dp.callback_query(F.data.startswith("sl_"))
async def set_lang(call: CallbackQuery):
    lc=call.data[3:]
    if lc not in LANGUAGES: return
    await db("UPDATE users SET language=? WHERE user_id=?",(lc,call.from_user.id))
    bi=await bot.get_me()
    await call.message.edit_text(BOT_TEXTS[lc]['lang_ok'])
    await call.message.answer(BOT_TEXTS[lc]['welcome'], reply_markup=main_menu(call.from_user.id,bi.username,lc))

@dp.callback_query(F.data.startswith("buy_"))
async def handle_buy(call: CallbackQuery):
    a=call.data[4:]
    if a not in PACKAGES: return
    price=PACKAGES[a]; coins=int(a); uid=call.from_user.id
    u=await get_user(uid); lang=u['language'] if u else 'pl'
    if not CRYPTO_TOKEN: await call.answer("Not configured",show_alert=True); return
    try:
        import aiohttp
        async with aiohttp.ClientSession() as s:
            r=await s.post("https://pay.crypt.bot/api/createInvoice",json={
                "currency_type":"fiat","fiat":"USD","amount":str(price),
                "description":f"Lucky Slots: {coins} {BOT_TEXTS[lang]['token']}",
                "payload":json.dumps({"user_id":uid,"coins":coins,"price_usd":price}),
                "paid_btn_name":"callback",
                "paid_btn_url":f"https://t.me/{(await bot.get_me()).username}"
            },headers={"Crypto-Pay-API-Token":CRYPTO_TOKEN})
            d=await r.json()
            if not d.get("ok"): await call.answer("Error",show_alert=True); return
            inv_id = str(d["result"].get("invoice_id",""))
            # Record pending payment
            await record_payment(uid, "deposit", price, coins, method="crypto_bot", status="pending", invoice_id=inv_id, details=f"package={coins}")
            kb=InlineKeyboardBuilder(); kb.button(text=f"💳 {price} USDT", url=d["result"]["mini_app_invoice_url"])
            await call.message.edit_text(BOT_TEXTS[lang]['pay_pending'], reply_markup=kb.as_markup())
    except Exception as e: logging.error(f"Pay: {e}"); await call.answer("Unavailable",show_alert=True)

# ==================== API ====================
H={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,POST,OPTIONS","Access-Control-Allow-Headers":"*"}
async def opts(r): return web.Response(headers=H)

async def api_balance(req):
    uid=get_uid(query=dict(req.rel_url.query))
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    await ensure_user(uid)
    await update_last_login(uid)
    u=await get_user(uid); v=vip_level(u['total_wagered'])
    cur = u['display_currency'] or 'USD'
    return web.json_response({"ok":True,
        "balance":u['coins'],  # legacy coins
        "balance_usdt_cents":u['balance_usdt_cents'],
        "balance_stars":u['balance_stars'],
        "display_currency":cur,
        "display_amount":usdt_cents_to_display(u['balance_usdt_cents'], cur),
        "currency_symbol":CURRENCY_SYMBOLS.get(cur,'$'),
        "free_spins":u['free_spins'],
        "stats":{"spins":u['total_spins'],"wagered":u['total_wagered'],"won":u['total_won'],"biggest":u['biggest_win']},
        "vip":{"name":v['name'],"icon":v['icon'],"cb":v['cb'],"wagered":u['total_wagered']},
        "refs":u['referrals_count']},headers=H)

async def api_spin(req):
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    bet=int(data.get("bet",0))
    if bet not in(5,10,25,50): return web.json_response({"ok":False,"error":"bad_bet"},headers=H)
    free=data.get("use_free_spin",False); u=await get_user(uid)
    is_free = False
    if free and u['free_spins']>0:
        await db("UPDATE users SET free_spins=free_spins-1 WHERE user_id=?",(uid,))
        is_free = True
    else:
        if u['coins']<bet: return web.json_response({"ok":False,"error":"funds","balance":u['coins']},headers=H)
        await add_coins(uid,-bet)
    r=base_spin(bet)
    if r["winnings"]>0: await add_coins(uid,r["winnings"])
    u2=await get_user(uid)
    # Record bet in history
    mult = r["winnings"]/bet if bet>0 else 0
    details = f"scatters={r['scatter_count']},bonus={'yes' if r['triggered_bonus'] else 'no'}"
    await record_bet(uid, "lucky_bonanza", "base_spin", bet, r["winnings"], u2['coins'], mult, is_free=is_free, details=details)
    await update_last_game(uid, "lucky_bonanza")
    return web.json_response({"ok":True,**r,"balance":u2['coins'],"free_spins":u2['free_spins']},headers=H)

async def api_bonus(req):
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    bet=int(data.get("bet",0)); mode=data.get("mode","triggered")
    if bet not in(5,10,25,50): return web.json_response({"ok":False,"error":"bad_bet"},headers=H)
    cost = 0
    if mode=="bought":
        cost=bet*100; u=await get_user(uid)
        if u['coins']<cost: return web.json_response({"ok":False,"error":"funds","balance":u['coins']},headers=H)
        await add_coins(uid,-cost)
    b=full_bonus(bet)
    if b["total_win"]>0: await add_coins(uid,b["total_win"])
    u2=await get_user(uid)
    # Record bonus round as a single bet entry
    actual_cost = cost if mode=="bought" else 0
    mult = b["total_win"]/actual_cost if actual_cost>0 else b["total_win"]/bet if bet>0 else 0
    details = f"mode={mode},spins={b['total_spins_played']},total_win={b['total_win']}"
    await record_bet(uid, "lucky_bonanza", "bonus_round", actual_cost or bet, b["total_win"], u2['coins'], mult, is_bonus=True, details=details)
    await update_last_game(uid, "lucky_bonanza")
    return web.json_response({"ok":True,**b,"balance":u2['coins']},headers=H)

async def api_wheel(req):
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    u=await get_user(uid); today=time.strftime("%Y-%m-%d")
    if u['last_wheel']==today: return web.json_response({"ok":False,"error":"done"},headers=H)
    prize=spin_wheel()
    await db("UPDATE users SET last_wheel=? WHERE user_id=?",(today,uid))
    if prize['type']=='coins':
        await add_coins(uid,prize['value'])
    else:
        await db("UPDATE users SET free_spins=free_spins+? WHERE user_id=?",(prize['value'],uid))
    u2=await get_user(uid)
    # Record wheel spin in bet_history (free, no wager)
    await record_bet(uid, "daily_wheel", "wheel_spin", 0, prize['value'] if prize['type']=='coins' else 0, u2['coins'], 0, details=f"prize={prize['type']}:{prize['value']}")
    return web.json_response({"ok":True,"prize":prize,"balance":u2['coins'],"free_spins":u2['free_spins']},headers=H)

async def api_wheel_status(req):
    uid=get_uid(query=dict(req.rel_url.query))
    if not uid: return web.json_response({"ok":False},headers=H)
    u=await get_user(uid); today=time.strftime("%Y-%m-%d")
    return web.json_response({"ok":True,"available":u['last_wheel']!=today},headers=H)

async def api_profile(req):
    uid=get_uid(query=dict(req.rel_url.query))
    if not uid: return web.json_response({"ok":False},headers=H)
    u=await get_user(uid); v=vip_level(u['total_wagered'])
    nxt=None
    for l in VIP_LEVELS:
        if l['min']>u['total_wagered']: nxt=l; break
    # Get recent bets (last 20)
    recent_bets = await db("SELECT game,bet_type,bet_amount,win_amount,profit,multiplier,is_bonus,created_at FROM bet_history WHERE user_id=? ORDER BY id DESC LIMIT 20", (uid,), fetch=True)
    bets_list = [dict(b) for b in recent_bets] if recent_bets else []
    # Get payment summary
    payments = await db("SELECT direction,amount_usd,amount_coins,method,created_at FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 20", (uid,), fetch=True)
    pay_list = [dict(p) for p in payments] if payments else []
    cur = u['display_currency'] or 'USD'
    return web.json_response({"ok":True,
        "username":u['username'] or '',"first_name":u['first_name'] or '',"last_name":u['last_name'] or '',
        "tg_language":u['tg_language_code'] or '',"is_premium":bool(u['is_premium']),
        "coins":u['coins'],"free_spins":u['free_spins'],
        "balance_usdt_cents":u['balance_usdt_cents'],
        "balance_stars":u['balance_stars'],
        "display_currency":cur,
        "display_amount":usdt_cents_to_display(u['balance_usdt_cents'], cur),
        "currency_symbol":CURRENCY_SYMBOLS.get(cur,'$'),
        "last_login":u['last_login'] or '',"last_game":u['last_game'] or '',
        "registered_at":u['created_at'] or '',
        "language":u['language'] or 'en',
        "vip":{"name":v['name'],"icon":v['icon'],"cb":v['cb'],"wagered":u['total_wagered'],
               "next":nxt['name'] if nxt else None,"next_at":nxt['min'] if nxt else None},
        "stats":{"spins":u['total_spins'],"wagered":u['total_wagered'],"won":u['total_won'],
                 "biggest":u['biggest_win'],"profit":u['total_won']-u['total_wagered'],
                 "deposited_usd":u['total_deposited_usd'],"withdrawn_usd":u['total_withdrawn_usd']},
        "refs":u['referrals_count'],
        "recent_bets":bets_list,
        "recent_payments":pay_list
    },headers=H)

async def api_webhook(req):
    try:
        body=await req.json()
        if body.get("update_type")!="invoice_paid": return web.json_response({"ok":True})
        pl=json.loads(body.get("payload",{}).get("payload","{}"))
        uid=pl.get("user_id"); price_usd=pl.get("amount_usd",0)
        usdt_cents = pl.get("usdt_cents", 0)
        coins=pl.get("coins",0)  # legacy support
        if not uid: return web.json_response({"ok":False})
        invoice_id = str(body.get("payload",{}).get("invoice_id",""))
        amount_usd = price_usd or PACKAGES.get(str(coins), 0)
        # Try to update pending payment to completed
        existing = await db("SELECT id FROM payments WHERE user_id=? AND invoice_id=? AND status='pending' LIMIT 1", (uid, invoice_id), one=True)
        if existing:
            await db("UPDATE payments SET status='completed',created_at=? WHERE id=?", (_now(), existing['id']))
        else:
            await record_payment(uid, "deposit", amount_usd, usdt_cents or coins, method="crypto_bot", status="completed", invoice_id=invoice_id)
        # Credit balance
        if usdt_cents > 0:
            # New system: credit USDT cents
            bal = await add_usdt(uid, usdt_cents)
            await db("UPDATE users SET total_deposited_usd=total_deposited_usd+? WHERE user_id=?", (amount_usd, int(uid)))
            logging.info(f"💳 USDT deposit OK: uid={uid}, +{usdt_cents}c (${amount_usd}), bal={bal}c")
        elif coins > 0:
            # Legacy: credit coins
            bal = await add_coins(uid, coins)
            await db("UPDATE users SET total_deposited_usd=total_deposited_usd+? WHERE user_id=?", (amount_usd, int(uid)))
            logging.info(f"💳 Coins deposit OK: uid={uid}, +{coins} coins, ${amount_usd}, bal={bal}")
        u=await get_user(uid); lang=u['language'] if u else 'pl'
        try:
            if usdt_cents > 0:
                await bot.send_message(uid, f"✅ +${usdt_cents/100:.2f} USDT!")
            else:
                await bot.send_message(uid, BOT_TEXTS[lang]['pay_success'].format(amount=coins,balance=bal))
        except: pass
        return web.json_response({"ok":True})
    except Exception as e: logging.error(f"WH: {e}", exc_info=True); return web.json_response({"ok":False})

async def api_set_currency(req):
    """POST /api/set-currency — change display currency"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    cur = data.get("currency","USD").upper()
    if cur not in CURRENCY_RATES: return web.json_response({"ok":False,"error":"invalid_currency"},headers=H)
    await db("UPDATE users SET display_currency=? WHERE user_id=?",(cur,uid))
    u=await get_user(uid)
    return web.json_response({"ok":True,"display_currency":cur,
        "display_amount":usdt_cents_to_display(u['balance_usdt_cents'], cur),
        "currency_symbol":CURRENCY_SYMBOLS.get(cur,'$')},headers=H)

async def api_set_language(req):
    """POST /api/set-language — change language from miniapp"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    lang = data.get("language","en")
    if lang not in LANGUAGES: return web.json_response({"ok":False,"error":"invalid_lang"},headers=H)
    await db("UPDATE users SET language=? WHERE user_id=?",(lang,uid))
    return web.json_response({"ok":True,"language":lang},headers=H)

async def api_create_deposit(req):
    """POST /api/create-deposit — create payment (CryptoBot USDT or Telegram Stars)"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    method = data.get("method","cryptobot")  # cryptobot | stars | card
    amount = data.get("amount", 0)
    u = await get_user(uid); lang = u['language'] if u else 'en'

    if method == "stars":
        # Telegram Stars — return stars_amount for client to call tg.openInvoice
        stars_count = int(amount)
        if stars_count not in STARS_PACKAGES.values() and stars_count <= 0:
            return web.json_response({"ok":False,"error":"invalid_amount"},headers=H)
        # Stars are handled client-side via Telegram.WebApp.openInvoice
        # We just return confirmation; the actual crediting happens via stars webhook
        return web.json_response({"ok":True,"method":"stars","stars_amount":stars_count,
            "description":f"RubyBet: {stars_count} ⭐ Stars"},headers=H)

    elif method == "cryptobot":
        # CryptoBot USDT deposit
        amount_usd = float(amount)
        if amount_usd < 1.0: return web.json_response({"ok":False,"error":"min_1_usd"},headers=H)
        if not CRYPTO_TOKEN: return web.json_response({"ok":False,"error":"not_configured"},headers=H)
        try:
            import aiohttp
            async with aiohttp.ClientSession() as s:
                usdt_cents = int(round(amount_usd * 100))
                r = await s.post("https://pay.crypt.bot/api/createInvoice", json={
                    "currency_type":"fiat","fiat":"USD","amount":str(amount_usd),
                    "description":f"RubyBet: ${amount_usd:.2f} USDT deposit",
                    "payload":json.dumps({"user_id":uid,"usdt_cents":usdt_cents,"amount_usd":amount_usd}),
                    "paid_btn_name":"callback",
                    "paid_btn_url":f"https://t.me/{(await bot.get_me()).username}"
                }, headers={"Crypto-Pay-API-Token":CRYPTO_TOKEN})
                d = await r.json()
                if not d.get("ok"): return web.json_response({"ok":False,"error":"invoice_failed"},headers=H)
                inv_id = str(d["result"].get("invoice_id",""))
                pay_url = d["result"]["mini_app_invoice_url"]
                await record_payment(uid, "deposit", amount_usd, usdt_cents, method="crypto_bot", status="pending", invoice_id=inv_id)
                return web.json_response({"ok":True,"method":"cryptobot","pay_url":pay_url,"invoice_id":inv_id},headers=H)
        except Exception as e:
            logging.error(f"CryptoBot deposit error: {e}")
            return web.json_response({"ok":False,"error":"service_unavailable"},headers=H)

    elif method == "card":
        # Placeholder for card payments — would integrate Stripe/etc
        return web.json_response({"ok":False,"error":"card_not_yet_available"},headers=H)

    return web.json_response({"ok":False,"error":"unknown_method"},headers=H)

async def api_stars_webhook(req):
    """POST /api/stars-webhook — called after successful Telegram Stars payment"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    data = await req.json(); uid = get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    stars = int(data.get("stars",0))
    if stars <= 0: return web.json_response({"ok":False,"error":"invalid"},headers=H)
    bal = await add_stars(uid, stars)
    await record_payment(uid, "deposit", 0, stars, method="telegram_stars", status="completed", details=f"stars={stars}")
    logging.info(f"⭐ Stars deposit: uid={uid}, +{stars} stars, bal={bal}")
    return web.json_response({"ok":True,"balance_stars":bal},headers=H)

async def api_currencies(req):
    """GET /api/currencies — return available currencies and rates"""
    return web.json_response({"ok":True,
        "currencies":[{"code":c,"rate":r,"symbol":CURRENCY_SYMBOLS.get(c,c)} for c,r in CURRENCY_RATES.items()]
    },headers=H)

async def start_api():
    app=web.Application()
    for path,handler in [("/api/balance",api_balance),("/api/wheel-status",api_wheel_status),("/api/profile",api_profile),("/api/currencies",api_currencies)]:
        app.router.add_get(path,handler)
    for path,handler in [("/api/spin",api_spin),("/api/bonus",api_bonus),("/api/wheel",api_wheel),("/api/crypto-webhook",api_webhook),("/api/set-currency",api_set_currency),("/api/set-language",api_set_language),("/api/create-deposit",api_create_deposit),("/api/stars-webhook",api_stars_webhook)]:
        app.router.add_post(path,handler)
    # Admin API (protected by bot token in query)
    app.router.add_get("/admin/stats",admin_stats)
    app.router.add_get("/admin/users",admin_users)
    app.router.add_get("/admin/user/{uid}",admin_user_detail)
    app.router.add_get("/admin/bets/{uid}",admin_user_bets)
    app.router.add_get("/admin/payments/{uid}",admin_user_payments)
    app.router.add_options("/{tail:.*}",opts)
    app.router.add_get("/health",lambda r:web.json_response({"ok":True}))
    runner=web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner,"0.0.0.0",API_PORT).start()
    logging.info(f"🚀 API :{API_PORT}")

# ==================== ADMIN API ====================
def _admin_check(req):
    """Simple admin auth: ?key=BOT_TOKEN_first_16_chars"""
    key = req.rel_url.query.get("key","")
    return key == BOT_TOKEN[:16]

async def admin_stats(req):
    """GET /admin/stats?key=... — глобальная статистика платформы"""
    if not _admin_check(req): return web.json_response({"ok":False,"error":"forbidden"},headers=H)
    total_users = await db("SELECT COUNT(*) as cnt FROM users", one=True)
    active_today = await db("SELECT COUNT(*) as cnt FROM users WHERE last_login LIKE ?", (time.strftime("%Y-%m-%d")+"%",), one=True)
    active_week = await db("SELECT COUNT(*) as cnt FROM users WHERE last_login >= date('now','-7 days')", one=True)
    total_bets = await db("SELECT COUNT(*) as cnt, COALESCE(SUM(bet_amount),0) as wagered, COALESCE(SUM(win_amount),0) as won FROM bet_history", one=True)
    total_deposits = await db("SELECT COUNT(*) as cnt, COALESCE(SUM(amount_usd),0) as usd, COALESCE(SUM(amount_coins),0) as coins FROM payments WHERE direction='deposit' AND status='completed'", one=True)
    total_referrals = await db("SELECT COALESCE(SUM(referrals_count),0) as cnt FROM users", one=True)
    top_winners = await db("SELECT user_id,username,first_name,total_won,total_wagered,biggest_win FROM users ORDER BY total_won DESC LIMIT 10", fetch=True)
    top_depositors = await db("SELECT user_id,username,first_name,total_deposited_usd,coins FROM users WHERE total_deposited_usd>0 ORDER BY total_deposited_usd DESC LIMIT 10", fetch=True)
    return web.json_response({"ok":True,
        "users":{"total":total_users['cnt'],"active_today":active_today['cnt'],"active_week":active_week['cnt']},
        "bets":{"total":total_bets['cnt'],"wagered":total_bets['wagered'],"won":total_bets['won'],"house_profit":total_bets['wagered']-total_bets['won']},
        "deposits":{"total":total_deposits['cnt'],"usd":round(total_deposits['usd'],2),"coins":total_deposits['coins']},
        "referrals":total_referrals['cnt'],
        "top_winners":[dict(r) for r in top_winners] if top_winners else [],
        "top_depositors":[dict(r) for r in top_depositors] if top_depositors else [],
    },headers=H)

async def admin_users(req):
    """GET /admin/users?key=...&limit=50&offset=0&sort=created_at — список всех юзеров"""
    if not _admin_check(req): return web.json_response({"ok":False,"error":"forbidden"},headers=H)
    limit = min(int(req.rel_url.query.get("limit",50)),200)
    offset = int(req.rel_url.query.get("offset",0))
    sort = req.rel_url.query.get("sort","created_at")
    allowed_sorts = {"created_at","last_login","total_wagered","total_deposited_usd","coins","total_spins"}
    if sort not in allowed_sorts: sort = "created_at"
    rows = await db(f"SELECT user_id,username,first_name,last_name,tg_language_code,is_premium,coins,total_wagered,total_won,total_deposited_usd,total_withdrawn_usd,total_spins,biggest_win,referrals_count,last_login,last_game,last_bot_interaction,created_at FROM users ORDER BY {sort} DESC LIMIT ? OFFSET ?", (limit,offset), fetch=True)
    total = await db("SELECT COUNT(*) as cnt FROM users", one=True)
    return web.json_response({"ok":True,"total":total['cnt'],"users":[dict(r) for r in rows] if rows else []},headers=H)

async def admin_user_detail(req):
    """GET /admin/user/{uid}?key=... — полная инфа по одному юзеру"""
    if not _admin_check(req): return web.json_response({"ok":False,"error":"forbidden"},headers=H)
    uid = int(req.match_info['uid'])
    u = await get_user(uid)
    if not u: return web.json_response({"ok":False,"error":"not_found"},headers=H)
    v = vip_level(u['total_wagered'])
    # Bet stats by game
    game_stats = await db("SELECT game,COUNT(*) as cnt,SUM(bet_amount) as wagered,SUM(win_amount) as won,SUM(profit) as profit,MAX(win_amount) as best FROM bet_history WHERE user_id=? GROUP BY game", (uid,), fetch=True)
    # Payment summary
    dep_total = await db("SELECT COUNT(*) as cnt,COALESCE(SUM(amount_usd),0) as usd,COALESCE(SUM(amount_coins),0) as coins FROM payments WHERE user_id=? AND direction='deposit' AND status='completed'", (uid,), one=True)
    return web.json_response({"ok":True,"user":dict(u),"vip":{"name":v['name'],"icon":v['icon'],"level_cb":v['cb']},
        "game_stats":[dict(g) for g in game_stats] if game_stats else [],
        "deposit_summary":dict(dep_total) if dep_total else {},
    },headers=H)

async def admin_user_bets(req):
    """GET /admin/bets/{uid}?key=...&limit=100 — история ставок юзера"""
    if not _admin_check(req): return web.json_response({"ok":False,"error":"forbidden"},headers=H)
    uid = int(req.match_info['uid'])
    limit = min(int(req.rel_url.query.get("limit",100)),500)
    rows = await db("SELECT * FROM bet_history WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid,limit), fetch=True)
    total = await db("SELECT COUNT(*) as cnt FROM bet_history WHERE user_id=?", (uid,), one=True)
    return web.json_response({"ok":True,"total":total['cnt'],"bets":[dict(r) for r in rows] if rows else []},headers=H)

async def admin_user_payments(req):
    """GET /admin/payments/{uid}?key=...&limit=100 — история платежей юзера"""
    if not _admin_check(req): return web.json_response({"ok":False,"error":"forbidden"},headers=H)
    uid = int(req.match_info['uid'])
    limit = min(int(req.rel_url.query.get("limit",100)),500)
    rows = await db("SELECT * FROM payments WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid,limit), fetch=True)
    total = await db("SELECT COUNT(*) as cnt FROM payments WHERE user_id=?", (uid,), one=True)
    return web.json_response({"ok":True,"total":total['cnt'],"payments":[dict(r) for r in rows] if rows else []},headers=H)

async def main():
    init_db(); await start_api(); await dp.start_polling(bot)

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    asyncio.run(main())
