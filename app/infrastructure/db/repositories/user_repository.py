import logging
from datetime import datetime, timezone
from app.infrastructure.db.pool import db

def _now():
    return datetime.now(timezone.utc)

async def get_user(uid: int, req_id: str = None):
    return await db("SELECT * FROM users WHERE user_id=$1", (int(uid),), one=True, req_id=req_id)

async def register_user(uid, username, first_name, last_name, is_premium, lang_code, req_id=None):
    await db(
        "INSERT INTO users(user_id,username,first_name,last_name,is_premium,tg_language_code,created_at,last_login) "
        "VALUES($1,$2,$3,$4,$5,$6,$7,$8)",
        (int(uid), username, first_name, last_name, 1 if is_premium else 0, lang_code, _now(), _now()),
        req_id=req_id
    )

async def update_user_activity(uid, un=None, fn=None, ln=None, lang_code=None, is_prem=False, req_id=None):
    await db(
        "UPDATE users SET username=COALESCE($1,username), first_name=COALESCE($2,first_name), "
        "last_name=COALESCE($3,last_name), tg_language_code=COALESCE($4,tg_language_code), "
        "is_premium=$5, last_bot_interaction=$6 WHERE user_id=$7",
        (un, fn, ln, lang_code, 1 if is_prem else 0, _now(), int(uid)),
        req_id=req_id
    )

async def update_last_login(uid, req_id=None):
    await db("UPDATE users SET last_login=$1 WHERE user_id=$2", (_now(), int(uid)), req_id=req_id)

async def update_last_game(uid, game_name, req_id=None):
    await db("UPDATE users SET last_game=$1 WHERE user_id=$2", (game_name, int(uid)), req_id=req_id)

async def set_language(uid, lang_code, req_id=None):
    await db("UPDATE users SET language=$1 WHERE user_id=$2", (lang_code, int(uid)), req_id=req_id)

async def set_referred_by(uid, rid, req_id=None):
    await db("UPDATE users SET referred_by=$1 WHERE user_id=$2 AND referred_by IS NULL", (int(rid), int(uid)), req_id=req_id)

async def increment_referrals(uid, bonus_cents, req_id=None):
    await db("UPDATE users SET referrals_count=referrals_count+1, balance_cents=balance_cents+$1 WHERE user_id=$2", (bonus_cents, int(uid)), req_id=req_id)
