import logging
from datetime import datetime, timezone
from app.infrastructure.db.pool import db

def _now():
    return datetime.now(timezone.utc)

async def record_bet(uid, game, bet_type, bet_amount, win_amount, balance_after, multiplier=0, is_bonus=False, is_free=False, details="", req_id=None):
    profit = win_amount - bet_amount
    await db(
        "INSERT INTO bet_history(user_id,game,bet_type,bet_amount,win_amount,profit,balance_after,multiplier,is_bonus,is_free_spin,details,created_at) "
        "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)",
        (int(uid), game, bet_type, bet_amount, win_amount, profit, balance_after, multiplier, 1 if is_bonus else 0, 1 if is_free else 0, details, _now()),
        req_id=req_id
    )
    # Update aggregates in users table
    await db(
        "UPDATE users SET total_spins=total_spins+1, total_wagered=total_wagered+$1, "
        "total_won=total_won+$2, biggest_win=GREATEST(biggest_win, $3) WHERE user_id=$4",
        (bet_amount, win_amount, win_amount, int(uid)),
        req_id=req_id
    )

async def get_recent_bets(uid: int, limit: int = 20, req_id: str = None):
    return await db(
        "SELECT game,bet_type,bet_amount,win_amount,profit,multiplier,is_bonus,created_at FROM bet_history "
        "WHERE user_id=$1 ORDER BY id DESC LIMIT $2",
        (int(uid), limit), fetch=True, req_id=req_id
    )

async def decrement_free_spins(uid: int, amount: int = 1, req_id: str = None):
    await db("UPDATE users SET free_spins=GREATEST(0, free_spins-$1) WHERE user_id=$2", (amount, int(uid)), req_id=req_id)

async def increment_free_spins(uid: int, amount: int, req_id: str = None):
    await db("UPDATE users SET free_spins=free_spins+$1 WHERE user_id=$2", (amount, int(uid)), req_id=req_id)
