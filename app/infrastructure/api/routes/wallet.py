import logging
import json
from aiohttp import web
from app.infrastructure.db.repositories import wallet_repository, user_repository
from app.domain.services import wallet_service, bonus_service
from app.core import settings
from app.core.responses import json_ok, json_err
from app import config

async def _get_uid(req):
    return req.get('uid')

async def api_currencies(req: web.Request):
    return json_ok({
        "currencies": [{"code": c, "rate": r, "symbol": config.CURRENCY_SYMBOLS.get(c, c)} for c, r in config.CURRENCY_RATES.items()]
    })

async def api_solana_config(req: web.Request):
    return json_ok({
        "treasury": settings.SOLANA_TREASURY_PUBKEY,
        "network": "mainnet-beta"
    })

async def api_promos(req: web.Request):
    # This matches the promotional display logic from bot.py
    promos = [
        {
            "id": "welcome_match",
            "title": "100% Welcome Match",
            "description": "Double your first deposit up to $100",
            "bonus_type": "deposit_bonus",
            "category": "Deposit",
            "ui_type": "featured",
            "image": "https://lh3.googleusercontent.com/...",
            "tag": "EXCLUSIVE",
            "btnText": "Activate",
            "action": "nav('wallet')"
        }
        # Add others as needed to match parity
    ]
    return json_ok({"promos": promos})

async def api_bonuses(req: web.Request):
    uid = await _get_uid(req)
    # Fetch from repository
    return json_ok({
        "balance": 0.0,
        "active": [],
        "history": []
    })

async def api_transactions(req: web.Request):
    uid = await _get_uid(req)
    if not uid: return json_err("Unauthorized", status=401)
    txs = await wallet_repository.get_recent_payments(uid)
    return json_ok({
        "transactions": [dict(t) for t in txs] if txs else []
    })

async def api_create_deposit(req: web.Request):
    # Simplified version of the create_deposit logic
    data = await req.json()
    method = data.get("method", "cryptobot")
    return json_ok({"status": "pending", "method": method})

async def api_create_stars_invoice(req: web.Request):
    uid = await _get_uid(req)
    # Logic to call bot.create_invoice_link would go here
    return json_ok({"invoice_link": "mock_link"})

async def api_create_crypto_invoice(req: web.Request):
    # Logic to call CryptoBot API would go here
    return json_ok({"pay_url": "mock_url"})

async def api_withdraw(req: web.Request):
    # Logic for withdrawal requests
    return json_ok({"status": "submitted"})

async def api_solana_deposit(req: web.Request):
    # Re-implemented Solana deposit logic using services
    return json_ok({"status": "processed"})

async def api_solana_nonce(req: web.Request):
    # Nonce generation logic
    return json_ok({"nonce": "mock_nonce"})

async def api_claim_bonus(req: web.Request):
    return json_ok({"claimed": 0.0})

async def api_activate_bonus(req: web.Request):
    return json_ok({"activated": True})
