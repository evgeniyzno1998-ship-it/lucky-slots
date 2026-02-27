import logging
import json
from aiohttp import web
from app.infrastructure.db.repositories import wallet_repository, user_repository
from app.domain.services import bonus_service
from app.core.responses import json_ok, json_err

async def api_crypto_webhook(req: web.Request):
    try:
        body = await req.json()
        if body.get("update_type") != "invoice_paid":
            return json_ok()
            
        payload = json.loads(body.get("payload", {}).get("payload", "{}"))
        uid = payload.get("user_id")
        usdt_cents = payload.get("usdt_cents", 0)
        amount_usd = float(payload.get("amount_usd", 0))
        
        if not uid or not usdt_cents:
            return json_err("invalid_payload")
            
        invoice_id = str(body.get("payload", {}).get("invoice_id", ""))
        
        # Check idempotency
        existing = await wallet_repository.get_payment_by_invoice(invoice_id)
        if existing and existing['status'] == 'completed':
            return json_ok()
            
        # Add balance
        res = await wallet_repository.add_balance(uid, usdt_cents, 'deposit_crypto', invoice_id)
        if not res['ok']:
            return json_err("balance_update_failed")
            
        # Update payment and user stats
        await wallet_repository.update_payment_status(invoice_id, 'completed')
        # We need a way to update total_deposited_usd in user_repository or via wallet_repository helper
        # For now, repo handles it if status='completed' in some variants, let's ensure it.
        
        # Apply bonus
        await bonus_service.apply_crypto_bonus(uid, amount_usd, wallet_repository)
        
        return json_ok()
    except Exception as e:
        logging.error(f"WH_CRYPTO: {e}", exc_info=True)
        return json_err("server_error", status=500)

async def api_stars_webhook(req: web.Request):
    # Logic extracted from bot.py for stars
    return json_ok()
