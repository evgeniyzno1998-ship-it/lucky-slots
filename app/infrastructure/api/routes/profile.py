import logging
from aiohttp import web
from app.infrastructure.db.repositories import user_repository, wallet_repository, game_repository
from app.domain.services import user_service, wallet_service
from app.core.responses import json_ok, json_err
from app import config

async def _get_uid(req):
    return req.get('uid')

async def api_balance(req: web.Request):
    uid = await _get_uid(req)
    req_id = req.get('req_id')
    if not uid: return json_err("unauthorized", status=401, req_id=req_id)

    u = await user_repository.get_user(uid, req_id=req_id)
    if not u: return json_err("user_not_found", status=404, req_id=req_id)

    v = user_service.get_vip_level(u['total_wagered'])
    cur = u.get('display_currency', 'USD')

    return json_ok({
        "balance": int(u['balance_cents']),
        "display_currency": cur,
        "display_amount": wallet_service.usdt_cents_to_display(u['balance_cents'], cur),
        "currency_symbol": config.CURRENCY_SYMBOLS.get(cur, '$'),
        "free_spins": int(u['free_spins']),
        "stats": {
            "spins": u['total_spins'],
            "wagered": u['total_wagered'],
            "won": u['total_won'],
            "biggest": u['biggest_win']
        },
        "vip": {
            "name": v['name'],
            "icon": v['icon'],
            "cb": v['cb'],
            "wagered": u['total_wagered']
        },
        "refs": int(u['referrals_count'])
    }, req_id=req_id)

async def api_profile(req: web.Request):
    uid = await _get_uid(req)
    req_id = req.get('req_id')
    if not uid: return json_err("unauthorized", status=401, req_id=req_id)

    u = await user_repository.get_user(uid)
    if not u: return json_err("user_not_found", status=404, req_id=req_id)

    v = user_service.get_vip_level(u['total_wagered'])
    cur = u.get('display_currency', 'USD')

    recent_bets = await game_repository.get_recent_bets(uid)
    recent_payments = await wallet_repository.get_recent_payments(uid)

    return json_ok({
        "username": u['username'] or '',
        "first_name": u['first_name'] or '',
        "last_name": u['last_name'] or '',
        "balance": int(u['balance_cents']),
        "free_spins": int(u['free_spins']),
        "display_currency": cur,
        "display_amount": wallet_service.usdt_cents_to_display(u['balance_cents'], cur),
        "currency_symbol": config.CURRENCY_SYMBOLS.get(cur, '$'),
        "vip": {
            "name": v['name'],
            "icon": v['icon'],
            "cb": v['cb'],
            "wagered": u['total_wagered']
        },
        "recent_bets": [dict(b) for b in recent_bets] if recent_bets else [],
        "recent_payments": [dict(p) for p in recent_payments] if recent_payments else []
    }, req_id=req_id)

async def api_notifications(req: web.Request):
    uid = await _get_uid(req)
    if not uid: return json_err("unauthorized", status=401)
    return json_ok({"notifications": [], "unread": 0})

async def api_notifications_read(req: web.Request):
    uid = await _get_uid(req)
    if not uid: return json_err("unauthorized", status=401)
    return json_ok({})

async def api_set_currency(req: web.Request):
    uid = await _get_uid(req)
    req_id = req.get('req_id')
    if not uid: return json_err("unauthorized", status=401, req_id=req_id)
    data = await req.json()
    cur = data.get("currency", "USD").upper()
    if cur not in config.CURRENCY_RATES:
        return json_err("invalid_currency", status=400, req_id=req_id)

    await user_repository.db("UPDATE users SET display_currency=$1 WHERE user_id=$2", (cur, uid))
    u = await user_repository.get_user(uid)

    return json_ok({
        "display_currency": cur,
        "display_amount": wallet_service.usdt_cents_to_display(u['balance_cents'], cur),
        "currency_symbol": config.CURRENCY_SYMBOLS.get(cur, '$')
    }, req_id=req_id)

async def api_set_language(req: web.Request):
    uid = await _get_uid(req)
    req_id = req.get('req_id')
    if not uid: return json_err("unauthorized", status=401, req_id=req_id)
    data = await req.json()
    lang = data.get("language", "en")
    if lang not in config.LANGUAGES:
        return json_err("invalid_lang", status=400, req_id=req_id)

    await user_repository.set_language(uid, lang)
    return json_ok({"language": lang}, req_id=req_id)
