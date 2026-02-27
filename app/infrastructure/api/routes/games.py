import logging
from aiohttp import web
from app.infrastructure.db.repositories import game_repository, user_repository, wallet_repository
from app.domain.services import game_service
from app.core.responses import json_ok, json_err
from app import config

async def _get_uid(req):
    return req.get('uid')

async def api_top_winnings(req: web.Request):
    # Logic for leaderboard
    return json_ok({"winners": []})

async def api_spin(req: web.Request):
    uid = await _get_uid(req)
    req_id = req.get('req_id')
    if not uid: return json_err("Unauthorized", status=401)
    
    data = await req.json()
    bet = int(data.get("bet", 0))
    dc = data.get("double_chance", False)
    actual_bet = int(bet * 1.25) if dc else bet
    
    if bet not in (5, 10, 25, 50):
        return json_err("bad_bet", req_id=req_id)
    
    u = await user_repository.get_user(uid)
    free_req = data.get("use_free_spin", False)
    is_free = False
    
    if free_req and u['free_spins'] > 0:
        await game_repository.decrement_free_spins(uid)
        is_free = True
    else:
        if u['balance_cents'] < actual_bet:
            return json_err("funds", message=str(u['balance_cents']), status=400, req_id=req_id)
        await wallet_repository.add_balance(uid, -actual_bet, 'bet_slots', 'slots_spin', req_id=req_id)
        
    r = game_service.base_spin(bet, double_chance=dc)
    if r["winnings"] > 0:
        await wallet_repository.add_balance(uid, r["winnings"], 'win_slots', 'slots_spin_win', req_id=req_id)
        
    u2 = await user_repository.get_user(uid)
    
    # Record
    mult = r["winnings"] / bet if bet > 0 else 0
    details = f"scatters={r['scatter_count']},bonus={'yes' if r['triggered_bonus'] else 'no'}"
    await game_repository.record_bet(uid, "lucky_bonanza", "base_spin", bet, r["winnings"], u2['balance_cents'], mult, is_free=is_free, details=details, req_id=req_id)
    await user_repository.update_last_game(uid, "lucky_bonanza")
    
    return json_ok({**r, "balance": u2['balance_cents'], "free_spins": u2['free_spins']}, req_id=req_id)

async def api_bonus_spin(req: web.Request):
    uid = await _get_uid(req)
    if not uid: return json_err("Unauthorized", status=401)
    # Similar to api_spin but calls full_bonus
    return json_ok({"status": "todo"})

async def api_wheel_spin(req: web.Request):
    uid = await _get_uid(req)
    if not uid: return json_err("Unauthorized", status=401)
    prize = game_service.spin_wheel()
    # Credit prize
    return json_ok({"prize": prize})

async def api_wheel_status(req: web.Request):
    uid = await _get_uid(req)
    if not uid: return json_err("Unauthorized", status=401)
    return json_ok({"available": True})
