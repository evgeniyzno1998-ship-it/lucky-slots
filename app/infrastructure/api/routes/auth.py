import logging
import json
from aiohttp import web
from app.core import security, settings
from app.infrastructure.db.repositories import user_repository
from app.domain.services import user_service, wallet_service
from app import config

async def api_auth(req: web.Request):
    req_id = req.get('req_id')
    try:
        try:
            data = await req.json()
        except Exception:
            return web.json_response({
                "ok": False,
                "error": {"code": "invalid_json", "message": "Malformed JSON payload"}
            }, status=400)
            
        init_data = data.get("init_data")
        if not init_data:
            return web.json_response({
                "ok": False,
                "error": {"code": "missing_init_data", "message": "Missing init_data field"}
            }, status=400)
        
        # 1. Validate Telegram Signature
        params = security.validate_telegram_data(init_data)
        if not params:
            return web.json_response({
                "ok": False,
                "error": {"code": "unauthorized", "message": "Invalid or expired Telegram signature"}
            }, status=401)
            
        user_json = params.get("user")
        if not user_json:
            return web.json_response({
                "ok": False,
                "error": {"code": "invalid_payload", "message": "Telegram payload missing 'user' object"}
            }, status=400)
            
        user_data = json.loads(user_json)
        uid = user_data.get("id")
        if uid is None:
            return web.json_response({
                "ok": False,
                "error": {"code": "missing_user_id", "message": "Telegram user object missing 'id'"}
            }, status=400)
            
        # 2. Database Action
        u = await user_repository.get_user(uid, req_id=req_id)
        if not u:
            # Auto-registration
            un = user_data.get("username", "")
            fn = user_data.get("first_name", "User")
            ln = user_data.get("last_name", "")
            is_prem = bool(user_data.get("is_premium", False))
            lang = user_data.get("language_code", "en")
            
            await user_repository.register_user(uid, un, fn, ln, is_prem, lang, req_id=req_id)
            u = await user_repository.get_user(uid, req_id=req_id)

        # 3. Session Generation
        uname = u['username'] or f"user_{uid}"
        token = security.generate_jwt({"uid": uid, "username": uname, "role": "user"})
        
        await user_repository.update_last_login(uid, req_id=req_id)
        
        # 4. Response Composition
        v = user_service.get_vip_level(u['total_wagered'])
        cur = u.get('display_currency', 'USD')
        
        return web.json_response({
            "ok": True,
            "data": {
                "session_token": token,
                "user": {
                    "id": uid,
                    "username": uname,
                    "first_name": u['first_name'],
                    "last_name": u['last_name'],
                    "language": u['language'] or 'en',
                    "vip": {"name": v['name'], "icon": v['icon'], "level": 0} # Simplified level per original
                },
                "wallet": {
                    "balance": int(u['balance_cents']),
                    "bonus_balance": 0,
                    "currency": cur,
                    "symbol": config.CURRENCY_SYMBOLS.get(cur, '$'),
                    "rate": config.CURRENCY_RATES.get(cur, 1.0)
                }
            }
        })
    except Exception as e:
        logging.error(f"[API_AUTH] Fatal error: {e}", exc_info=True)
        return web.json_response({
            "ok": False,
            "error": {"code": "server_error", "message": "Internal server error"}
        }, status=500)
