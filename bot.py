import logging, sqlite3, asyncio, os, json, urllib.parse, hashlib, hmac, random, time, math
import jwt as pyjwt
import bcrypt
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, LabeledPrice
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
JWT_SECRET = os.getenv("JWT_SECRET", BOT_TOKEN[:32] if BOT_TOKEN else "change-me-in-production")
JWT_EXPIRY_HOURS = 24
ADMIN_DEFAULT_PASSWORD = os.getenv("ADMIN_PASSWORD", "rubybet2024")

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
            admin_note TEXT DEFAULT '',
            is_blocked INTEGER DEFAULT 0,
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
            ("admin_note","TEXT DEFAULT ''"),
            ("is_blocked","INTEGER DEFAULT 0"),
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

        # === USER_BONUSES — personal bonus assignments ===
        c.execute('''CREATE TABLE IF NOT EXISTS user_bonuses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bonus_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            icon TEXT DEFAULT 'redeem',
            amount REAL DEFAULT 0,
            progress REAL DEFAULT 0,
            max_progress REAL DEFAULT 0,
            vip_tag TEXT DEFAULT '',
            expires_at TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            badge TEXT DEFAULT '',
            claimed_at TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )''')
        try: c.execute("CREATE INDEX IF NOT EXISTS idx_bonuses_user ON user_bonuses(user_id)")
        except: pass

        # === BONUS_TEMPLATES ===
        c.execute('''CREATE TABLE IF NOT EXISTS bonus_templates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bonus_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        # === BONUS_CAMPAIGNS ===
        c.execute('''CREATE TABLE IF NOT EXISTS bonus_campaigns(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            bonus_type TEXT NOT NULL,
            template_id INTEGER,
            target_segment TEXT NOT NULL,
            total_players INTEGER DEFAULT 0,
            claimed_players INTEGER DEFAULT 0,
            notification_sent INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')

        # === ADMIN_USERS — dashboard operators ===
        c.execute('''CREATE TABLE IF NOT EXISTS admin_users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT DEFAULT '',
            role TEXT DEFAULT 'viewer',
            permissions TEXT DEFAULT '[]',
            is_active INTEGER DEFAULT 1,
            created_by INTEGER DEFAULT NULL,
            last_login TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Add sample templates if none exist
        if not c.execute("SELECT COUNT(*) FROM bonus_templates").fetchone()[0]:
            c.executemany("INSERT INTO bonus_templates(name, bonus_type, amount, description) VALUES(?,?,?,?)", [
                ("Welcome Pack 100%", "deposit_bonus", 100.0, "100% bonus on first deposit up to $100"),
                ("VIP Weekly Cashback", "cashback", 50.0, "Weekly 10% cashback for VIP players"),
                ("Reactivation Spins", "free_spins", 20.0, "20 free spins for inactive users")
            ])
        # Create default owner if no admins exist
        existing = c.execute("SELECT COUNT(*) as cnt FROM admin_users").fetchone()
        if existing and existing[0] == 0:
            pw_hash = bcrypt.hashpw(ADMIN_DEFAULT_PASSWORD.encode(), bcrypt.gensalt()).decode()
            c.execute(
                "INSERT INTO admin_users(username,password_hash,display_name,role,permissions) VALUES(?,?,?,?,?)",
                ('owner', pw_hash, 'Owner', 'owner', json.dumps(['*']))
            )
            logging.info(f"🔑 Default admin created: username='owner', password='{ADMIN_DEFAULT_PASSWORD}'")

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
        # Auto-assign welcome bonuses for new user
        await assign_welcome_bonuses(int(uid))
        return True
    else:
        await db(
            "UPDATE users SET username=COALESCE(?,username),first_name=COALESCE(?,first_name),last_name=COALESCE(?,last_name),tg_language_code=COALESCE(?,tg_language_code),is_premium=?,last_bot_interaction=? WHERE user_id=?",
            (un, fn, ln, lang_code, 1 if is_prem else 0, _now(), int(uid))
        )
    return False

async def assign_welcome_bonuses(uid):
    """Assign default bonuses for a new user."""
    bonuses = [
        ("cashback", "Weekly Cashback", "Earn 10% back on all weekly losses", "payments", 0, 0, 100, "", "", "active", "CASHBACK"),
        ("free_spins", "Welcome Free Spins", "50 Free Spins on Ruby Slots for new players", "casino", 50, 0, 0, "", "", "active", "FREE SPINS"),
        ("deposit_match", "100% Deposit Match", "Double your first deposit up to $50", "redeem", 50, 0, 200, "", "", "active", "DEPOSIT MATCH"),
    ]
    for b in bonuses:
        await db(
            "INSERT INTO user_bonuses(user_id,bonus_type,title,description,icon,amount,progress,max_progress,vip_tag,expires_at,status,badge) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (uid, *b)
        )

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
                "description":f"RubyBet: {coins} {BOT_TEXTS[lang]['token']}",
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

# ==================== TELEGRAM STARS PAYMENTS ====================
@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    """Always approve pre-checkout for Stars payments."""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(msg: Message):
    """Handle successful Telegram Stars payment."""
    payment = msg.successful_payment
    uid = msg.from_user.id
    try:
        pl = json.loads(payment.invoice_payload)
        stars = pl.get("stars", 0)
        if stars > 0:
            bal = await add_stars(uid, stars)
            await record_payment(uid, "deposit", 0, stars, method="telegram_stars", status="completed", details=f"stars={stars},charge_id={payment.telegram_payment_charge_id}")
            logging.info(f"⭐ Stars payment OK: uid={uid}, +{stars} stars, bal={bal}")
            u = await get_user(uid); lang = u['language'] if u else 'en'
            await msg.answer(f"✅ +{stars} ⭐ Stars!\n⭐ Balance: {bal}")
    except Exception as e:
        logging.error(f"Stars payment handler error: {e}")

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

async def api_bonuses(req):
    """GET /api/bonuses — get user's personal bonuses (active + history)"""
    uid = get_uid(query=dict(req.rel_url.query))
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    
    # Get active bonuses
    active = await db("SELECT * FROM user_bonuses WHERE user_id=? AND status='active' ORDER BY created_at DESC", (uid,), fetch=True)
    # Get history (completed/expired)
    history = await db("SELECT * FROM user_bonuses WHERE user_id=? AND status IN ('completed','expired') ORDER BY created_at DESC LIMIT 20", (uid,), fetch=True)
    # Calculate total claimable
    total_claimable = 0
    active_list = []
    for b in (active or []):
        bd = dict(b)
        if bd['bonus_type'] == 'cashback' and bd['progress'] > 0:
            total_claimable += bd['progress']
        active_list.append(bd)
    
    return web.json_response({"ok":True,
        "balance": round(total_claimable, 2),
        "active": active_list,
        "history": [dict(h) for h in history] if history else []
    },headers=H)

async def api_claim_bonus(req):
    """POST /api/claim-bonus — claim a specific bonus"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    data = await req.json(); uid = get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    bonus_id = int(data.get("bonus_id", 0))
    if not bonus_id: return web.json_response({"ok":False,"error":"invalid_bonus"},headers=H)
    
    b = await db("SELECT * FROM user_bonuses WHERE id=? AND user_id=? AND status='active'", (bonus_id, uid), one=True)
    if not b: return web.json_response({"ok":False,"error":"bonus_not_found"},headers=H)
    
    # Credit the bonus amount
    claim_amount = b['progress'] if b['bonus_type'] == 'cashback' else b['amount']
    if claim_amount > 0:
        usdt_cents = int(round(claim_amount * 100))
        await add_usdt(uid, usdt_cents)
        await record_payment(uid, "deposit", claim_amount, usdt_cents, method="bonus_claim", status="completed", details=f"bonus_id={bonus_id},type={b['bonus_type']}")
    
    # Mark bonus as completed
    await db("UPDATE user_bonuses SET status='completed',claimed_at=? WHERE id=?", (_now(), bonus_id))
    
    u = await get_user(uid)
    return web.json_response({"ok":True,"claimed":claim_amount,"balance_usdt_cents":u['balance_usdt_cents']},headers=H)

async def api_activate_bonus(req):
    """POST /api/activate-bonus — activate a pending bonus (e.g. free spins)"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    data = await req.json(); uid = get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    bonus_id = int(data.get("bonus_id", 0))
    
    b = await db("SELECT * FROM user_bonuses WHERE id=? AND user_id=? AND status='active'", (bonus_id, uid), one=True)
    if not b: return web.json_response({"ok":False,"error":"bonus_not_found"},headers=H)
    
    # For free spins bonus, credit spins
    if b['bonus_type'] == 'free_spins':
        spins = int(b['amount']) if b['amount'] else 50
        await db("UPDATE users SET free_spins=free_spins+? WHERE user_id=?", (spins, uid))
        await db("UPDATE user_bonuses SET status='completed',claimed_at=? WHERE id=?", (_now(), bonus_id))
        u = await get_user(uid)
        return web.json_response({"ok":True,"free_spins_added":spins,"free_spins":u['free_spins']},headers=H)
    
    return web.json_response({"ok":True,"activated":True},headers=H)

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

async def api_create_stars_invoice(req):
    """POST /api/create-stars-invoice — create Telegram Stars invoice for purchase"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    stars = int(data.get("stars", 50))
    if stars <= 0: return web.json_response({"ok":False,"error":"invalid_amount"},headers=H)
    
    # Create Telegram Stars invoice via Bot API
    try:
        from aiogram.types import LabeledPrice
        prices = [LabeledPrice(label=f"RubyBet {stars} Stars", amount=stars)]
        # Create invoice link that can be opened via tg.openInvoice()
        link = await bot.create_invoice_link(
            title=f"RubyBet: {stars} ⭐ Stars",
            description=f"Purchase {stars} Stars for RubyBet casino",
            payload=json.dumps({"user_id": uid, "stars": stars, "type": "stars"}),
            currency="XTR",  # Telegram Stars currency code
            prices=prices
        )
        return web.json_response({"ok":True,"invoice_link":link,"stars":stars},headers=H)
    except Exception as e:
        logging.error(f"Stars invoice error: {e}")
        return web.json_response({"ok":False,"error":str(e)},headers=H)

async def api_create_crypto_invoice(req):
    """POST /api/create-invoice — create CryptoBot USDT invoice (legacy endpoint)"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    coins = int(data.get("coins", 50))
    amount = float(data.get("amount", PACKAGES.get(str(coins), 0.50)))
    if amount <= 0: return web.json_response({"ok":False,"error":"invalid_amount"},headers=H)
    if not CRYPTO_TOKEN: return web.json_response({"ok":False,"error":"not_configured"},headers=H)
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as s:
            usdt_cents = int(round(amount * 100))
            r = await s.post("https://pay.crypt.bot/api/createInvoice", json={
                "currency_type":"fiat","fiat":"USD","amount":str(amount),
                "description":f"RubyBet: ${amount:.2f} deposit",
                "payload":json.dumps({"user_id":uid,"usdt_cents":usdt_cents,"coins":coins,"amount_usd":amount}),
                "paid_btn_name":"callback",
                "paid_btn_url":f"https://t.me/{(await bot.get_me()).username}"
            }, headers={"Crypto-Pay-API-Token":CRYPTO_TOKEN})
            d = await r.json()
            if not d.get("ok"): return web.json_response({"ok":False,"error":"invoice_failed"},headers=H)
            inv_id = str(d["result"].get("invoice_id",""))
            pay_url = d["result"]["mini_app_invoice_url"]
            await record_payment(uid, "deposit", amount, usdt_cents or coins, method="crypto_bot", status="pending", invoice_id=inv_id)
            return web.json_response({"ok":True,"pay_url":pay_url,"invoice_id":inv_id},headers=H)
    except Exception as e:
        logging.error(f"CryptoBot invoice error: {e}")
        return web.json_response({"ok":False,"error":"service_unavailable"},headers=H)

async def api_create_card_payment(req):
    """POST /api/create-card-payment — placeholder for card payments"""
    if req.method=="OPTIONS": return web.Response(headers=H)
    return web.json_response({"ok":False,"error":"card_not_yet_available"},headers=H)

async def start_api():
    app=web.Application()
    for path,handler in [("/api/balance",api_balance),("/api/wheel-status",api_wheel_status),("/api/profile",api_profile),("/api/currencies",api_currencies),("/api/bonuses",api_bonuses)]:
        app.router.add_get(path,handler)
    for path,handler in [("/api/spin",api_spin),("/api/bonus",api_bonus),("/api/wheel",api_wheel),("/api/crypto-webhook",api_webhook),("/api/set-currency",api_set_currency),("/api/set-language",api_set_language),("/api/create-deposit",api_create_deposit),("/api/stars-webhook",api_stars_webhook),("/api/create-stars-invoice",api_create_stars_invoice),("/api/create-invoice",api_create_crypto_invoice),("/api/create-card-payment",api_create_card_payment),("/api/claim-bonus",api_claim_bonus),("/api/activate-bonus",api_activate_bonus)]:
        app.router.add_post(path,handler)
    # Admin API routes (JWT protected)
    # Admin API (GET)
    for path, handler in [
        ("/admin/auth/me", admin_auth_me),
        ("/admin/auth/users", admin_auth_list),
        ("/admin/stats", admin_stats),
        ("/admin/users", admin_users),
        ("/admin/user/{uid}", admin_user_detail),
        ("/admin/bets/{uid}", admin_user_bets),
        ("/admin/payments/{uid}", admin_user_payments),
        ("/admin/games", admin_games),
        ("/admin/financial", admin_financial),
        ("/admin/cohorts", admin_cohorts),
        ("/admin/live", admin_live),
        ("/admin/affiliates", admin_affiliates),
        ("/admin/bonus-stats", admin_bonus_stats),
        ("/admin/bonus/templates", admin_bonus_templates_get),
        ("/admin/bonus/campaigns", admin_bonus_campaigns_get),
    ]:
        app.router.add_get(path, handler)
    # Admin API (POST)
    for path, handler in [
        ("/admin/auth/login", admin_auth_login),
        ("/admin/auth/create", admin_auth_create),
        ("/admin/auth/update", admin_auth_update),
        ("/admin/auth/delete", admin_auth_delete),
        ("/admin/bonus/templates", admin_bonus_templates_post),
        ("/admin/bonus/issue", admin_bonus_issue),
        ("/admin/user/{uid}/update", admin_player_update),
        ("/admin/user/{uid}/note", admin_player_note),
    ]:
        app.router.add_post(path, handler)
    app.router.add_options("/{tail:.*}",opts)
    app.router.add_get("/health",lambda r:web.json_response({"ok":True}))
    runner=web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner,"0.0.0.0",API_PORT).start()
    logging.info(f"🚀 API :{API_PORT}")

# ==================== ADMIN AUTH (JWT + RBAC) ====================
ADMIN_SECTIONS = ['dashboard','live_monitor','players','cohorts','games','financial','risk_fraud','compliance','affiliates','bonus_analytics','bonus_management','marketing','settings']

def _jwt_encode(admin_id, username, role, permissions):
    payload = {
        "sub": str(admin_id),
        "username": username,
        "role": role,
        "permissions": permissions,
        "exp": int(time.time()) + JWT_EXPIRY_HOURS * 3600,
        "iat": int(time.time()),
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")

def _jwt_decode(token):
    try:
        return pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_exp": True})
    except pyjwt.ExpiredSignatureError:
        logging.warning("JWT expired")
        return None
    except pyjwt.InvalidTokenError as e:
        logging.warning(f"JWT invalid: {e}")
        return None
    except Exception as e:
        logging.error(f"JWT decode error: {e}")
        return None

def _get_admin_from_req(req):
    """Extract and verify JWT from Authorization header or ?key= fallback."""
    auth = req.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        payload = _jwt_decode(token)
        if payload:
            return payload
        else:
            logging.warning(f"JWT decode returned None for token: {token[:20]}...")
    # Legacy fallback: ?key=BOT_TOKEN[:16]
    key = req.rel_url.query.get("key","")
    if key == BOT_TOKEN[:16]:

        return {"sub": 0, "username": "legacy", "role": "owner", "permissions": ["*"]}
    return None

def _has_permission(admin, section):
    """Check if admin has access to a section."""
    if not admin:
        return False
    if admin.get("role") == "owner":
        return True
    perms = admin.get("permissions", [])
    if isinstance(perms, str):
        try: perms = json.loads(perms)
        except: perms = []
    return "*" in perms or section in perms

def _require_admin(req, section=None):
    """Returns admin payload or error response."""
    admin = _get_admin_from_req(req)
    if not admin:
        return None, web.json_response({"ok": False, "error": "unauthorized"}, status=401, headers=H)
    if section and not _has_permission(admin, section):
        return None, web.json_response({"ok": False, "error": "forbidden", "required": section}, status=403, headers=H)
    return admin, None

# --- Auth Endpoints ---
async def admin_auth_login(req):
    """POST /admin/auth/login — authenticate admin user, return JWT."""
    if req.method == "OPTIONS": return web.Response(headers=H)
    data = await req.json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    if not username or not password:
        return web.json_response({"ok": False, "error": "missing_credentials"}, headers=H)

    with _conn() as c:
        row = c.execute("SELECT * FROM admin_users WHERE username=? AND is_active=1", (username,)).fetchone()
    if not row:
        return web.json_response({"ok": False, "error": "invalid_credentials"}, headers=H)

    if not bcrypt.checkpw(password.encode(), row['password_hash'].encode()):
        return web.json_response({"ok": False, "error": "invalid_credentials"}, headers=H)

    perms = json.loads(row['permissions']) if row['permissions'] else []
    token = _jwt_encode(row['id'], row['username'], row['role'], perms)

    # Update last_login
    with _conn() as c:
        c.execute("UPDATE admin_users SET last_login=? WHERE id=?", (_now(), row['id']))

    return web.json_response({"ok": True, "token": token, "admin": {
        "id": row['id'], "username": row['username'], "display_name": row['display_name'],
        "role": row['role'], "permissions": perms,
    }}, headers=H)

async def admin_auth_me(req):
    """GET /admin/auth/me — get current admin profile."""
    admin, err = _require_admin(req)
    if err: return err
    return web.json_response({"ok": True, "admin": admin}, headers=H)

async def admin_auth_list(req):
    """GET /admin/auth/users — list all admin accounts (owner/admin only)."""
    admin, err = _require_admin(req, "settings")
    if err: return err
    if admin['role'] not in ('owner', 'admin'):
        return web.json_response({"ok": False, "error": "forbidden"}, status=403, headers=H)
    with _conn() as c:
        rows = c.execute("SELECT id,username,display_name,role,permissions,is_active,last_login,created_at FROM admin_users ORDER BY id").fetchall()
    return web.json_response({"ok": True, "admins": [dict(r) for r in rows] if rows else []}, headers=H)

async def admin_auth_create(req):
    """POST /admin/auth/create — create new admin user (owner only)."""
    if req.method == "OPTIONS": return web.Response(headers=H)
    admin, err = _require_admin(req, "settings")
    if err: return err
    if admin['role'] != 'owner':
        return web.json_response({"ok": False, "error": "owner_only"}, status=403, headers=H)
    data = await req.json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")
    display_name = data.get("display_name", username)
    role = data.get("role", "viewer")
    permissions = data.get("permissions", [])
    if not username or not password:
        return web.json_response({"ok": False, "error": "missing_fields"}, headers=H)
    if role not in ('admin', 'manager', 'viewer'):
        return web.json_response({"ok": False, "error": "invalid_role"}, headers=H)
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO admin_users(username,password_hash,display_name,role,permissions,created_by) VALUES(?,?,?,?,?,?)",
                (username, pw_hash, display_name, role, json.dumps(permissions), admin['sub'])
            )
        return web.json_response({"ok": True, "message": f"Admin '{username}' created"}, headers=H)
    except sqlite3.IntegrityError:
        return web.json_response({"ok": False, "error": "username_exists"}, headers=H)

async def admin_auth_update(req):
    """POST /admin/auth/update — update admin user (owner or self)."""
    if req.method == "OPTIONS": return web.Response(headers=H)
    admin, err = _require_admin(req, "settings")
    if err: return err
    
    data = await req.json()
    admin_id = int(data.get("id", 0))
    is_self = admin_id == int(admin['sub'])
    
    if admin['role'] != 'owner' and not is_self:
        return web.json_response({"ok": False, "error": "owner_only"}, status=403, headers=H)
        
    updates = []
    params = []
    
    # Only owner can change roles or permissions
    if "role" in data and data["role"] in ('admin', 'manager', 'viewer'):
        if admin['role'] == 'owner':
            updates.append("role=?"); params.append(data["role"])
    
    if "permissions" in data:
        if admin['role'] == 'owner':
            updates.append("permissions=?"); params.append(json.dumps(data["permissions"]))
            
    if "display_name" in data:
        updates.append("display_name=?"); params.append(data["display_name"])
        
    if "is_active" in data:
        if admin['role'] == 'owner':
            updates.append("is_active=?"); params.append(1 if data["is_active"] else 0)
            
    if "password" in data and data["password"]:
        pw_hash = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
        updates.append("password_hash=?"); params.append(pw_hash)
        
    if not updates:
        return web.json_response({"ok": False, "error": "nothing_to_update"}, headers=H)
        
    params.append(admin_id)
    with _conn() as c:
        c.execute(f"UPDATE admin_users SET {','.join(updates)} WHERE id=?", params)
    return web.json_response({"ok": True}, headers=H)

async def admin_auth_delete(req):
    """POST /admin/auth/delete — delete admin user (owner only)."""
    if req.method == "OPTIONS": return web.Response(headers=H)
    admin, err = _require_admin(req, "settings")
    if err: return err
    if admin['role'] != 'owner':
        return web.json_response({"ok": False, "error": "owner_only"}, status=403, headers=H)
    data = await req.json()
    admin_id = int(data.get("id", 0))
    # Can't delete self
    if admin_id == admin['sub']:
        return web.json_response({"ok": False, "error": "cannot_delete_self"}, headers=H)
    with _conn() as c:
        c.execute("DELETE FROM admin_users WHERE id=? AND role!='owner'", (admin_id,))
    return web.json_response({"ok": True}, headers=H)

# --- Data Endpoints (JWT protected) ---
async def admin_stats(req):
    """GET /admin/stats — platform overview."""
    admin, err = _require_admin(req, "dashboard")
    if err: return err
    total_users = await db("SELECT COUNT(*) as cnt FROM users", one=True)
    active_today = await db("SELECT COUNT(*) as cnt FROM users WHERE last_login LIKE ?", (time.strftime("%Y-%m-%d")+"%",), one=True)
    active_week = await db("SELECT COUNT(*) as cnt FROM users WHERE last_login >= date('now','-7 days')", one=True)
    new_today = await db("SELECT COUNT(*) as cnt FROM users WHERE created_at LIKE ?", (time.strftime("%Y-%m-%d")+"%",), one=True)
    total_bets = await db("SELECT COUNT(*) as cnt, COALESCE(SUM(bet_amount),0) as wagered, COALESCE(SUM(win_amount),0) as won FROM bet_history", one=True)
    today_bets = await db("SELECT COUNT(*) as cnt, COALESCE(SUM(bet_amount),0) as wagered, COALESCE(SUM(win_amount),0) as won FROM bet_history WHERE created_at LIKE ?", (time.strftime("%Y-%m-%d")+"%",), one=True)
    total_deposits = await db("SELECT COUNT(*) as cnt, COALESCE(SUM(amount_usd),0) as usd FROM payments WHERE direction='deposit' AND status='completed'", one=True)
    total_withdrawals = await db("SELECT COUNT(*) as cnt, COALESCE(SUM(amount_usd),0) as usd FROM payments WHERE direction='withdrawal' AND status='completed'", one=True)
    total_referrals = await db("SELECT COALESCE(SUM(referrals_count),0) as cnt FROM users", one=True)
    # Revenue per day (last 14 days)
    revenue_daily = await db("SELECT date(created_at) as day, SUM(bet_amount) as wagered, SUM(win_amount) as won, SUM(bet_amount)-SUM(win_amount) as ggr, COUNT(*) as bets FROM bet_history WHERE created_at >= date('now','-14 days') GROUP BY date(created_at) ORDER BY day", fetch=True)
    # Registrations per day (last 14 days)
    reg_daily = await db("SELECT date(created_at) as day, COUNT(*) as cnt FROM users WHERE created_at >= date('now','-14 days') GROUP BY date(created_at) ORDER BY day", fetch=True)
    top_winners = await db("SELECT user_id,username,first_name,total_won,total_wagered,biggest_win FROM users ORDER BY total_won DESC LIMIT 10", fetch=True)
    top_depositors = await db("SELECT user_id,username,first_name,total_deposited_usd,coins FROM users WHERE total_deposited_usd>0 ORDER BY total_deposited_usd DESC LIMIT 10", fetch=True)
    ggr = total_bets['wagered'] - total_bets['won']
    ggr_today = today_bets['wagered'] - today_bets['won']
    return web.json_response({"ok": True,
        "users": {"total": total_users['cnt'], "active_today": active_today['cnt'], "active_week": active_week['cnt'], "new_today": new_today['cnt']},
        "bets": {"total": total_bets['cnt'], "wagered": total_bets['wagered'], "won": total_bets['won'], "ggr": ggr, "today_bets": today_bets['cnt'], "today_wagered": today_bets['wagered'], "today_ggr": ggr_today},
        "deposits": {"total": total_deposits['cnt'], "usd": round(total_deposits['usd'], 2)},
        "withdrawals": {"total": total_withdrawals['cnt'], "usd": round(total_withdrawals['usd'], 2)},
        "net_revenue": round(total_deposits['usd'] - total_withdrawals['usd'], 2),
        "referrals": total_referrals['cnt'],
        "revenue_daily": [dict(r) for r in revenue_daily] if revenue_daily else [],
        "registrations_daily": [dict(r) for r in reg_daily] if reg_daily else [],
        "top_winners": [dict(r) for r in top_winners] if top_winners else [],
        "top_depositors": [dict(r) for r in top_depositors] if top_depositors else [],
    }, headers=H)

async def admin_users(req):
    """GET /admin/users — player list with filters."""
    admin, err = _require_admin(req, "players")
    if err: return err
    limit = min(int(req.rel_url.query.get("limit", 50)), 200)
    offset = int(req.rel_url.query.get("offset", 0))
    sort = req.rel_url.query.get("sort", "created_at")
    search = req.rel_url.query.get("search", "").strip()
    segment = req.rel_url.query.get("segment", "all")
    allowed_sorts = {"created_at","last_login","total_wagered","total_deposited_usd","coins","total_spins","balance_usdt_cents","balance_stars"}
    if sort not in allowed_sorts: sort = "created_at"
    where = "1=1"
    params = []
    if search:
        where += " AND (username LIKE ? OR first_name LIKE ? OR CAST(user_id AS TEXT) LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])
    if segment == "vip":
        where += " AND total_wagered >= 5000"
    elif segment == "new":
        where += " AND created_at >= date('now','-7 days')"
    elif segment == "churn_risk":
        where += " AND last_login < date('now','-14 days')"
    elif segment == "depositors":
        where += " AND total_deposited_usd > 0"
    rows = await db(f"SELECT user_id,username,first_name,last_name,is_premium,coins,balance_usdt_cents,balance_stars,total_wagered,total_won,total_deposited_usd,total_withdrawn_usd,total_spins,biggest_win,referrals_count,last_login,last_game,created_at FROM users WHERE {where} ORDER BY {sort} DESC LIMIT ? OFFSET ?", (*params, limit, offset), fetch=True)
    total = await db(f"SELECT COUNT(*) as cnt FROM users WHERE {where}", params, one=True)
    return web.json_response({"ok": True, "total": total['cnt'], "users": [dict(r) for r in rows] if rows else []}, headers=H)

async def admin_user_detail(req):
    """GET /admin/user/{uid} — full user info."""
    admin, err = _require_admin(req, "players")
    if err: return err
    uid = int(req.match_info['uid'])
    u = await get_user(uid)
    if not u: return web.json_response({"ok": False, "error": "not_found"}, headers=H)
    v = vip_level(u['total_wagered'])
    game_stats = await db("SELECT game,COUNT(*) as cnt,SUM(bet_amount) as wagered,SUM(win_amount) as won,SUM(profit) as profit,MAX(win_amount) as best FROM bet_history WHERE user_id=? GROUP BY game", (uid,), fetch=True)
    dep_total = await db("SELECT COUNT(*) as cnt,COALESCE(SUM(amount_usd),0) as usd FROM payments WHERE user_id=? AND direction='deposit' AND status='completed'", (uid,), one=True)
    bonuses = await db("SELECT * FROM user_bonuses WHERE user_id=? ORDER BY created_at DESC LIMIT 20", (uid,), fetch=True)
    return web.json_response({"ok": True, "user": dict(u), "vip": {"name": v['name'], "icon": v['icon'], "level_cb": v['cb']},
        "game_stats": [dict(g) for g in game_stats] if game_stats else [],
        "deposit_summary": dict(dep_total) if dep_total else {},
        "bonuses": [dict(b) for b in bonuses] if bonuses else [],
    }, headers=H)

async def admin_user_bets(req):
    """GET /admin/bets/{uid} — user bet history."""
    admin, err = _require_admin(req, "players")
    if err: return err
    uid = int(req.match_info['uid'])
    limit = min(int(req.rel_url.query.get("limit", 100)), 500)
    rows = await db("SELECT * FROM bet_history WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid, limit), fetch=True)
    total = await db("SELECT COUNT(*) as cnt FROM bet_history WHERE user_id=?", (uid,), one=True)
    return web.json_response({"ok": True, "total": total['cnt'], "bets": [dict(r) for r in rows] if rows else []}, headers=H)

async def admin_user_payments(req):
    """GET /admin/payments/{uid} — user payment history."""
    admin, err = _require_admin(req, "financial")
    if err: return err
    uid = int(req.match_info['uid'])
    limit = min(int(req.rel_url.query.get("limit", 100)), 500)
    rows = await db("SELECT * FROM payments WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid, limit), fetch=True)
    total = await db("SELECT COUNT(*) as cnt FROM payments WHERE user_id=?", (uid,), one=True)
    return web.json_response({"ok": True, "total": total['cnt'], "payments": [dict(r) for r in rows] if rows else []}, headers=H)

async def admin_player_update(req):
    """POST /admin/user/{uid}/update — update player stats/status."""
    admin, err = _require_admin(req, "players")
    if err: return err
    uid = int(req.match_info['uid'])
    data = await req.json()
    updates = []; params = []
    if "coins" in data:
        updates.append("coins=?"); params.append(int(data["coins"]))
    if "balance_usdt_cents" in data:
        updates.append("balance_usdt_cents=?"); params.append(int(data["balance_usdt_cents"]))
    if "free_spins" in data:
        updates.append("free_spins=?"); params.append(int(data["free_spins"]))
    if "is_blocked" in data:
        updates.append("is_blocked=?"); params.append(1 if data["is_blocked"] else 0)
    if not updates: return web.json_response({"ok": False, "error": "nothing_to_update"}, headers=H)
    params.append(uid)
    await db(f"UPDATE users SET {','.join(updates)} WHERE user_id=?", tuple(params))
    return web.json_response({"ok": True}, headers=H)

async def admin_player_note(req):
    """POST /admin/user/{uid}/note — save admin note for player."""
    admin, err = _require_admin(req, "players")
    if err: return err
    uid = int(req.match_info['uid'])
    data = await req.json()
    note = data.get("note", "").strip()
    await db("UPDATE users SET admin_note=? WHERE user_id=?", (note, uid))
    return web.json_response({"ok": True}, headers=H)

async def admin_games(req):
    """GET /admin/games — per-game analytics."""
    admin, err = _require_admin(req, "games")
    if err: return err
    games = await db("SELECT game, COUNT(*) as total_bets, COUNT(DISTINCT user_id) as unique_players, SUM(bet_amount) as wagered, SUM(win_amount) as won, SUM(bet_amount)-SUM(win_amount) as ggr, AVG(bet_amount) as avg_bet, MAX(win_amount) as biggest_win FROM bet_history GROUP BY game ORDER BY wagered DESC", fetch=True)
    # Per game per day (last 7 days)
    daily = await db("SELECT game, date(created_at) as day, COUNT(*) as bets, SUM(bet_amount) as wagered, SUM(win_amount) as won FROM bet_history WHERE created_at >= date('now','-7 days') GROUP BY game, date(created_at) ORDER BY day", fetch=True)
    return web.json_response({"ok": True,
        "games": [dict(g) for g in games] if games else [],
        "daily": [dict(d) for d in daily] if daily else [],
    }, headers=H)

async def admin_financial(req):
    """GET /admin/financial — deposits, withdrawals, GGR trends."""
    admin, err = _require_admin(req, "financial")
    if err: return err
    days = int(req.rel_url.query.get("days", 30))
    dep_daily = await db(f"SELECT date(created_at) as day, COUNT(*) as cnt, SUM(amount_usd) as usd, method FROM payments WHERE direction='deposit' AND status='completed' AND created_at >= date('now','-{days} days') GROUP BY date(created_at), method ORDER BY day", fetch=True)
    wd_daily = await db(f"SELECT date(created_at) as day, COUNT(*) as cnt, SUM(amount_usd) as usd FROM payments WHERE direction='withdrawal' AND status='completed' AND created_at >= date('now','-{days} days') GROUP BY date(created_at) ORDER BY day", fetch=True)
    ggr_daily = await db(f"SELECT date(created_at) as day, SUM(bet_amount)-SUM(win_amount) as ggr, SUM(bet_amount) as wagered, SUM(win_amount) as won FROM bet_history WHERE created_at >= date('now','-{days} days') GROUP BY date(created_at) ORDER BY day", fetch=True)
    # Totals
    totals = await db("SELECT COALESCE(SUM(CASE WHEN direction='deposit' THEN amount_usd ELSE 0 END),0) as deposits, COALESCE(SUM(CASE WHEN direction='withdrawal' THEN amount_usd ELSE 0 END),0) as withdrawals FROM payments WHERE status='completed'", one=True)
    # By method
    by_method = await db("SELECT method, COUNT(*) as cnt, SUM(amount_usd) as usd FROM payments WHERE direction='deposit' AND status='completed' GROUP BY method", fetch=True)
    return web.json_response({"ok": True,
        "deposits_daily": [dict(d) for d in dep_daily] if dep_daily else [],
        "withdrawals_daily": [dict(d) for d in wd_daily] if wd_daily else [],
        "ggr_daily": [dict(d) for d in ggr_daily] if ggr_daily else [],
        "totals": {"deposits": round(totals['deposits'], 2), "withdrawals": round(totals['withdrawals'], 2), "net": round(totals['deposits'] - totals['withdrawals'], 2)},
        "by_method": [dict(m) for m in by_method] if by_method else [],
    }, headers=H)

async def admin_cohorts(req):
    """GET /admin/cohorts — cohort analysis by registration date."""
    admin, err = _require_admin(req, "cohorts")
    if err: return err
    # Weekly cohorts for last 8 weeks
    cohorts = await db("""
        SELECT
            strftime('%Y-W%W', created_at) as cohort,
            COUNT(*) as size,
            SUM(CASE WHEN total_deposited_usd > 0 THEN 1 ELSE 0 END) as depositors,
            AVG(total_wagered) as avg_wagered,
            AVG(total_deposited_usd) as avg_deposit,
            SUM(total_deposited_usd) as total_ltv,
            SUM(CASE WHEN last_login >= date('now','-7 days') THEN 1 ELSE 0 END) as retained_7d
        FROM users WHERE created_at >= date('now','-56 days')
        GROUP BY strftime('%Y-W%W', created_at) ORDER BY cohort
    """, fetch=True)
    return web.json_response({"ok": True, "cohorts": [dict(c) for c in cohorts] if cohorts else []}, headers=H)

async def admin_live(req):
    """GET /admin/live — recent activity feed."""
    admin, err = _require_admin(req, "live_monitor")
    if err: return err
    limit = min(int(req.rel_url.query.get("limit", 50)), 200)
    recent_bets = await db("SELECT b.*, u.username, u.first_name FROM bet_history b LEFT JOIN users u ON b.user_id=u.user_id ORDER BY b.id DESC LIMIT ?", (limit,), fetch=True)
    recent_deps = await db("SELECT p.*, u.username, u.first_name FROM payments p LEFT JOIN users u ON p.user_id=u.user_id WHERE p.direction='deposit' AND p.status='completed' ORDER BY p.id DESC LIMIT 20", fetch=True)
    active_now = await db("SELECT COUNT(*) as cnt FROM users WHERE last_login >= datetime('now','-5 minutes')", one=True)
    return web.json_response({"ok": True,
        "recent_bets": [dict(r) for r in recent_bets] if recent_bets else [],
        "recent_deposits": [dict(r) for r in recent_deps] if recent_deps else [],
        "active_now": active_now['cnt'],
    }, headers=H)

async def admin_affiliates(req):
    """GET /admin/affiliates — referral stats."""
    admin, err = _require_admin(req, "affiliates")
    if err: return err
    top_refs = await db("SELECT user_id, username, first_name, referrals_count, total_deposited_usd FROM users WHERE referrals_count > 0 ORDER BY referrals_count DESC LIMIT 50", fetch=True)
    total = await db("SELECT COALESCE(SUM(referrals_count),0) as cnt, COUNT(CASE WHEN referrals_count>0 THEN 1 END) as referrers FROM users", one=True)
    return web.json_response({"ok": True,
        "top_referrers": [dict(r) for r in top_refs] if top_refs else [],
        "total_referrals": total['cnt'],
        "total_referrers": total['referrers'],
    }, headers=H)

async def admin_bonus_stats(req):
    """GET /admin/bonus-stats — bonus analytics."""
    admin, err = _require_admin(req, "bonus_analytics")
    if err: return err
    by_type = await db("SELECT bonus_type, status, COUNT(*) as cnt, SUM(amount) as total_amount FROM user_bonuses GROUP BY bonus_type, status", fetch=True)
    active = await db("SELECT COUNT(*) as cnt FROM user_bonuses WHERE status='active'", one=True)
    claimed = await db("SELECT COUNT(*) as cnt, COALESCE(SUM(amount),0) as total FROM user_bonuses WHERE status='completed'", one=True)
    return web.json_response({"ok": True,
        "by_type": [dict(r) for r in by_type] if by_type else [],
        "active_count": active['cnt'],
        "claimed_count": claimed['cnt'],
        "claimed_total": claimed['total'],
    }, headers=H)

async def admin_bonus_templates_get(req):
    """GET /admin/bonus/templates — list all templates."""
    admin, err = _require_admin(req, "bonus_management")
    if err: return err
    rows = await db("SELECT * FROM bonus_templates ORDER BY id DESC", fetch=True)
    return web.json_response({"ok": True, "templates": [dict(r) for r in rows] if rows else []}, headers=H)

async def admin_bonus_templates_post(req):
    """POST /admin/bonus/templates — create a new template."""
    admin, err = _require_admin(req, "bonus_management")
    if err: return err
    data = await req.json()
    name = data.get("name")
    btype = data.get("bonus_type")
    amount = float(data.get("amount", 0))
    desc = data.get("description", "")
    if not name or not btype: return web.json_response({"ok": False, "error": "missing_fields"}, headers=H)
    await db("INSERT INTO bonus_templates(name, bonus_type, amount, description) VALUES(?,?,?,?)", (name, btype, amount, desc))
    return web.json_response({"ok": True}, headers=H)

async def admin_bonus_campaigns_get(req):
    """GET /admin/bonus/campaigns — list all active campaigns."""
    admin, err = _require_admin(req, "bonus_management")
    if err: return err
    rows = await db("SELECT * FROM bonus_campaigns ORDER BY id DESC", fetch=True)
    return web.json_response({"ok": True, "campaigns": [dict(r) for r in rows] if rows else []}, headers=H)

async def admin_bonus_issue(req):
    """POST /admin/bonus/issue — send bonuses to players with notification support."""
    admin, err = _require_admin(req, "bonus_management")
    if err: return err
    data = await req.json()
    
    is_template = data.get("is_template", False)
    template_id = data.get("template_id")
    
    if is_template and template_id:
        tpl = await db("SELECT * FROM bonus_templates WHERE id=?", (template_id,), one=True)
        if not tpl: return web.json_response({"ok": False, "error": "template_not_found"}, headers=H)
        bonus_type = tpl['bonus_type']
        amount = tpl['amount']
        title = tpl['name']
        description = tpl['description']
    else:
        bonus_type = data.get("bonus_type", "free_spins")
        amount = float(data.get("amount", 0))
        title = data.get("title", "Special Bonus")
        description = data.get("description", "")

    target = data.get("target_segment", "all")
    send_notif = data.get("send_notification", False)
    notif_msg = data.get("notification_message", "You received a bonus!")

    # Find target users
    if target == "vip":
        rows = await db("SELECT user_id, first_name FROM users WHERE total_wagered >= 5000", fetch=True)
    elif target == "new":
        rows = await db("SELECT user_id, first_name FROM users WHERE created_at >= date('now','-7 days')", fetch=True)
    elif target == "churn_risk":
        rows = await db("SELECT user_id, first_name FROM users WHERE last_login <= date('now','-14 days')", fetch=True)
    else:
        rows = await db("SELECT user_id, first_name FROM users", fetch=True)
    
    targets = rows if rows else []
    
    # Create campaign record
    await db(
        "INSERT INTO bonus_campaigns(title, bonus_type, template_id, target_segment, total_players, notification_sent) VALUES(?,?,?,?,?,?)",
        (title, bonus_type, template_id if is_template else None, target, len(targets), 1 if send_notif else 0)
    )

    count = 0
    notif_count = 0
    for u in targets:
        uid = u['user_id']
        await db(
            "INSERT INTO user_bonuses(user_id,bonus_type,title,description,icon,amount,status,badge) VALUES(?,?,?,?,?,?,?,?)",
            (uid, bonus_type, title, description, "redeem", amount, "active", bonus_type.upper().replace("_", " "))
        )
        count += 1
        
        if send_notif:
            try:
                # Basic personalization
                personal_msg = notif_msg.replace("{name}", u['first_name'] or "Player")
                # Try to send via bot if it exists
                await bot.send_message(uid, personal_msg)
                notif_count += 1
            except Exception as e:
                logging.debug(f"Could not send push to {uid}: {e}")
            
    return web.json_response({"ok": True, "assigned_count": count, "notif_sent": notif_count}, headers=H)

async def main():
    init_db()
    await start_api()
    api_only = os.getenv("API_ONLY", "") == "1" or "--api-only" in sys.argv
    if api_only:
        logging.info("🖥️  Running in API-ONLY mode (no Telegram polling)")
        while True:
            await asyncio.sleep(3600)
    else:
        await dp.start_polling(bot)

if __name__=='__main__':
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    asyncio.run(main())


