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
        c.execute('''CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
            coins INTEGER DEFAULT 0, free_spins INTEGER DEFAULT 0,
            total_wagered INTEGER DEFAULT 0, total_won INTEGER DEFAULT 0,
            total_spins INTEGER DEFAULT 0, biggest_win INTEGER DEFAULT 0,
            referrals_count INTEGER DEFAULT 0, referred_by INTEGER DEFAULT NULL,
            language TEXT DEFAULT 'pl', last_wheel TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        for col, d in [("free_spins","INTEGER DEFAULT 0"),("total_wagered","INTEGER DEFAULT 0"),("total_won","INTEGER DEFAULT 0"),("total_spins","INTEGER DEFAULT 0"),("biggest_win","INTEGER DEFAULT 0"),("last_wheel","TEXT DEFAULT ''"),("created_at","TEXT DEFAULT CURRENT_TIMESTAMP"),("language","TEXT DEFAULT 'pl'"),("referred_by","INTEGER DEFAULT NULL")]:
            try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {d}")
            except: pass

async def db(q, p=(), fetch=False, one=False):
    async with _db_lock:
        def r():
            with _conn() as c:
                cur = c.execute(q, p)
                if one: return cur.fetchone()
                if fetch: return cur.fetchall()
        return await asyncio.get_event_loop().run_in_executor(None, r)

async def ensure_user(uid, un=None, fn=None):
    e = await db("SELECT user_id FROM users WHERE user_id=?", (int(uid),), one=True)
    if not e: await db("INSERT OR IGNORE INTO users(user_id,username,first_name) VALUES(?,?,?)", (int(uid), un, fn)); return True
    elif un or fn: await db("UPDATE users SET username=COALESCE(?,username),first_name=COALESCE(?,first_name) WHERE user_id=?", (un, fn, int(uid)))
    return False

async def get_user(uid):
    return await db("SELECT * FROM users WHERE user_id=?", (int(uid),), one=True)

async def add_coins(uid, d):
    await db("UPDATE users SET coins=MAX(0,coins+?) WHERE user_id=?", (d, int(uid)))
    r = await db("SELECT coins FROM users WHERE user_id=?", (int(uid),), one=True)
    return r['coins'] if r else 0

async def record_spin(uid, bet, win):
    await db("UPDATE users SET total_spins=total_spins+1,total_wagered=total_wagered+?,total_won=total_won+?,biggest_win=MAX(biggest_win,?) WHERE user_id=?", (bet, win, win, int(uid)))

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
    is_new=await ensure_user(uid, msg.from_user.username, msg.from_user.first_name)
    bi=await bot.get_me(); u=await get_user(uid); lang=u['language'] if u else 'pl'
    if len(args)>1 and args[1]=="deposit":
        await msg.answer(BOT_TEXTS[lang]['buy_m'], reply_markup=pkgs_kb(lang)); return
    if is_new and len(args)>1 and args[1].startswith("ref"):
        try:
            rid=int(args[1][3:])
            if rid!=uid:
                await db("UPDATE users SET referred_by=? WHERE user_id=? AND referred_by IS NULL",(rid,uid))
                await db("UPDATE users SET referrals_count=referrals_count+1,coins=coins+? WHERE user_id=?",(REFERRAL_BONUS,rid))
                await add_coins(uid,REFERRAL_BONUS)
                ru=await get_user(rid); rl=ru['language'] if ru else 'pl'
                try: await bot.send_message(rid, BOT_TEXTS[rl]['ref_earned'].format(bonus=REFERRAL_BONUS))
                except: pass
                await msg.answer(BOT_TEXTS[lang]['ref_welcome'].format(bonus=REFERRAL_BONUS))
        except: pass
    await msg.answer(BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(uid, bi.username, lang))

@dp.message(F.text)
async def handle_btn(msg: Message):
    uid=msg.from_user.id; txt=msg.text.strip()
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
            r=await s.post("https://pay.crypt.bot/api/createInvoice",json={"currency_type":"fiat","fiat":"USD","amount":str(price),"description":f"Lucky Slots: {coins} {BOT_TEXTS[lang]['token']}","payload":json.dumps({"user_id":uid,"coins":coins}),"paid_btn_name":"callback","paid_btn_url":f"https://t.me/{(await bot.get_me()).username}"},headers={"Crypto-Pay-API-Token":CRYPTO_TOKEN})
            d=await r.json()
            if not d.get("ok"): await call.answer("Error",show_alert=True); return
            kb=InlineKeyboardBuilder(); kb.button(text=f"💳 {price} USDT", url=d["result"]["mini_app_invoice_url"])
            await call.message.edit_text(BOT_TEXTS[lang]['pay_pending'], reply_markup=kb.as_markup())
    except Exception as e: logging.error(f"Pay: {e}"); await call.answer("Unavailable",show_alert=True)

# ==================== API ====================
H={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,POST,OPTIONS","Access-Control-Allow-Headers":"*"}
async def opts(r): return web.Response(headers=H)

async def api_balance(req):
    uid=get_uid(query=dict(req.rel_url.query))
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    await ensure_user(uid); u=await get_user(uid); v=vip_level(u['total_wagered'])
    return web.json_response({"ok":True,"balance":u['coins'],"free_spins":u['free_spins'],
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
    if free and u['free_spins']>0:
        await db("UPDATE users SET free_spins=free_spins-1 WHERE user_id=?",(uid,))
    else:
        if u['coins']<bet: return web.json_response({"ok":False,"error":"funds","balance":u['coins']},headers=H)
        await add_coins(uid,-bet)
    r=base_spin(bet)
    if r["winnings"]>0: await add_coins(uid,r["winnings"])
    await record_spin(uid,bet,r["winnings"])
    u2=await get_user(uid)
    return web.json_response({"ok":True,**r,"balance":u2['coins'],"free_spins":u2['free_spins']},headers=H)

async def api_bonus(req):
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    bet=int(data.get("bet",0)); mode=data.get("mode","triggered")
    if bet not in(5,10,25,50): return web.json_response({"ok":False,"error":"bad_bet"},headers=H)
    if mode=="bought":
        cost=bet*100; u=await get_user(uid)
        if u['coins']<cost: return web.json_response({"ok":False,"error":"funds","balance":u['coins']},headers=H)
        await add_coins(uid,-cost)
    b=full_bonus(bet)
    if b["total_win"]>0: await add_coins(uid,b["total_win"])
    await record_spin(uid,bet,b["total_win"])
    u2=await get_user(uid)
    return web.json_response({"ok":True,**b,"balance":u2['coins']},headers=H)

async def api_wheel(req):
    if req.method=="OPTIONS": return web.Response(headers=H)
    data=await req.json(); uid=get_uid(data)
    if not uid: return web.json_response({"ok":False,"error":"auth"},headers=H)
    u=await get_user(uid); today=time.strftime("%Y-%m-%d")
    if u['last_wheel']==today: return web.json_response({"ok":False,"error":"done"},headers=H)
    prize=spin_wheel()
    await db("UPDATE users SET last_wheel=? WHERE user_id=?",(today,uid))
    if prize['type']=='coins': await add_coins(uid,prize['value'])
    else: await db("UPDATE users SET free_spins=free_spins+? WHERE user_id=?",(prize['value'],uid))
    u2=await get_user(uid)
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
    return web.json_response({"ok":True,"username":u['username'] or '',"first_name":u['first_name'] or '',
        "coins":u['coins'],"free_spins":u['free_spins'],
        "vip":{"name":v['name'],"icon":v['icon'],"cb":v['cb'],"wagered":u['total_wagered'],
               "next":nxt['name'] if nxt else None,"next_at":nxt['min'] if nxt else None},
        "stats":{"spins":u['total_spins'],"wagered":u['total_wagered'],"won":u['total_won'],
                 "biggest":u['biggest_win'],"profit":u['total_won']-u['total_wagered']},
        "refs":u['referrals_count']},headers=H)

async def api_webhook(req):
    try:
        body=await req.json()
        if body.get("update_type")!="invoice_paid": return web.json_response({"ok":True})
        pl=json.loads(body.get("payload",{}).get("payload","{}"))
        uid,coins=pl.get("user_id"),pl.get("coins",0)
        if not uid or not coins: return web.json_response({"ok":False})
        bal=await add_coins(uid,coins); u=await get_user(uid); lang=u['language'] if u else 'pl'
        try: await bot.send_message(uid,BOT_TEXTS[lang]['pay_success'].format(amount=coins,balance=bal))
        except: pass
        return web.json_response({"ok":True})
    except Exception as e: logging.error(f"WH: {e}"); return web.json_response({"ok":False})

async def start_api():
    app=web.Application()
    for path,handler in [("/api/balance",api_balance),("/api/wheel-status",api_wheel_status),("/api/profile",api_profile)]:
        app.router.add_get(path,handler)
    for path,handler in [("/api/spin",api_spin),("/api/bonus",api_bonus),("/api/wheel",api_wheel),("/api/crypto-webhook",api_webhook)]:
        app.router.add_post(path,handler)
    app.router.add_options("/{tail:.*}",opts)
    app.router.add_get("/health",lambda r:web.json_response({"ok":True}))
    runner=web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner,"0.0.0.0",API_PORT).start()
    logging.info(f"🚀 API :{API_PORT}")

async def main():
    init_db(); await start_api(); await dp.start_polling(bot)

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    asyncio.run(main())
