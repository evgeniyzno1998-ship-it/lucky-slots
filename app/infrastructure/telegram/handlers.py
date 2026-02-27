from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
import urllib.parse
import json

from app.core import settings, security
from app.infrastructure.db.repositories import user_repository, wallet_repository
from app import config

def mktok(uid):
    # This matches the logic from bot.py if it existed there
    return security.generate_jwt({"uid": uid})

def main_menu(uid, bname, lang):
    t = config.BOT_TEXTS[lang]
    tok = mktok(uid)
    url = f"{settings.WEBAPP_URL}?api={urllib.parse.quote(settings.PUBLIC_URL, safe='')}&bot={bname}&lang={lang}&uid={uid}&token={tok}"
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t['play'], web_app=WebAppInfo(url=url))],
        [KeyboardButton(text=t['buy']), KeyboardButton(text=t['bal'])],
        [KeyboardButton(text=t['ref']), KeyboardButton(text=t['set'])]
    ], resize_keyboard=True)

def pkgs_kb(lang):
    t = config.BOT_TEXTS[lang]['token']
    b = InlineKeyboardBuilder()
    for a, p in config.PACKAGES.items():
        b.button(text=f"{a} {t} — {p} USDT", callback_data=f"buy_{a}")
    return b.adjust(1).as_markup()

async def cmd_start(msg: Message):
    uid = msg.from_user.id
    args = msg.text.split()
    u = msg.from_user
    
    # Check if user exists, else register
    usr = await user_repository.get_user(uid)
    is_new = False
    if not usr:
        await user_repository.register_user(uid, u.username, u.first_name, u.last_name, bool(getattr(u, 'is_premium', False)), u.language_code or 'en')
        usr = await user_repository.get_user(uid)
        is_new = True
    
    # Update activity
    await user_repository.update_user_activity(uid, u.username, u.first_name, u.last_name, u.language_code, bool(getattr(u, 'is_premium', False)))
    
    lang = usr['language'] if usr else 'en'
    bot_info = await msg.bot.get_me()
    
    if len(args) > 1 and args[1] == "deposit":
        await msg.answer(config.BOT_TEXTS[lang]['buy_m'], reply_markup=pkgs_kb(lang))
        return
        
    await msg.answer(config.BOT_TEXTS[lang]['welcome'], reply_markup=main_menu(uid, bot_info.username, lang))

async def handle_message(msg: Message):
    uid = msg.from_user.id
    txt = msg.text.strip()
    usr = await user_repository.get_user(uid)
    if not usr: return
    
    lang = usr['language'] or 'en'
    bot_info = await msg.bot.get_me()
    
    if any(txt == config.BOT_TEXTS[l]['buy'] for l in config.BOT_TEXTS):
        await msg.answer(config.BOT_TEXTS[lang]['buy_m'], reply_markup=pkgs_kb(lang))
    elif any(txt == config.BOT_TEXTS[l]['bal'] for l in config.BOT_TEXTS):
        cur = usr.get('display_currency', 'USD')
        # Display balance logic here
        pass
    elif any(txt == config.BOT_TEXTS[l]['ref'] for l in config.BOT_TEXTS):
        # Referral logic here
        pass
    elif any(txt == config.BOT_TEXTS[l]['set'] for l in config.BOT_TEXTS):
        kb = InlineKeyboardBuilder()
        for c, n in config.LANGUAGES.items():
            kb.button(text=n, callback_data=f"sl_{c}")
        await msg.answer("🌐", reply_markup=kb.adjust(2).as_markup())

async def handle_callback(call: CallbackQuery):
    # Logic from bot.py callback handlers
    pass

async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

async def process_successful_payment(msg: Message):
    # Stars logic here
    pass
