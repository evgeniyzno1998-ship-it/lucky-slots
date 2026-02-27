import logging
from aiohttp import web
from app.infrastructure.db.repositories import user_repository, wallet_repository, game_repository
from app.domain.services import user_service, wallet_service
from app import config

async def _get_uid(req):
    # This will be replaced by a middleware that decoes JWT
    # For now, we'll mock it or use the one from request items if we add it
    return req.get('uid')

async def api_balance(req: web.Request):
    uid = await _get_uid(req)
    req_id = req.get('req_id')
    if not uid: return web.json_response({"ok": False}, status=401)
    
    u = await user_repository.get_user(uid, req_id=req_id)
    if not u: return web.json_response({"ok": False, "error": "user_not_found"}, status=404)
    
    v = user_service.get_vip_level(u['total_wagered'])
    cur = u.get('display_currency', 'USD')
    
    return web.json_response({
        "ok": True,
        "data": {
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
        }
    })

async def api_profile(req: web.Request):
    uid = await _get_uid(req)
    if not uid: return web.json_response({"ok": False}, status=401)
    
    u = await user_repository.get_user(uid)
    if not u: return web.json_response({"ok": False}, status=404)
    
    v = user_service.get_vip_level(u['total_wagered'])
    cur = u.get('display_currency', 'USD')
    
    # Get recent data
    recent_bets = await game_repository.get_recent_bets(uid)
    recent_payments = await wallet_repository.get_recent_payments(uid)
    
    return web.json_response({
        "ok": True,
        "data": {
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
        }
    })

async def api_notifications(req: web.Request):
    # logic from bot.py
    pass

async def api_notifications_read(req: web.Request):
    # logic from bot.py
    pass

async def api_set_currency(req: web.Request):
    uid = await _get_uid(req)
    data = await req.json()
    cur = data.get("currency", "USD").upper()
    if cur not in config.CURRENCY_RATES: return web.json_response({"ok": False, "error": "invalid_currency"}, status=400)
    
    # We should add this to user_repository
    await user_repository.db("UPDATE users SET display_currency=$1 WHERE user_id=$2", (cur, uid))
    u = await user_repository.get_user(uid)
    
    return web.json_response({
        "ok": True,
        "data": {
            "display_currency": cur,
            "display_amount": wallet_service.usdt_cents_to_display(u['balance_cents'], cur),
            "currency_symbol": config.CURRENCY_SYMBOLS.get(cur, '$')
        }
    })

async def api_set_language(req: web.Request):
    uid = await _get_uid(req)
    data = await req.json()
    lang = data.get("language", "en")
    if lang not in config.LANGUAGES: return web.json_response({"ok": False, "error": "invalid_lang"}, status=400)
    
    await user_repository.set_language(uid, lang)
    return web.json_response({"ok": True, "data": {"language": lang}})
