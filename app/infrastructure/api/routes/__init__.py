from aiohttp import web
from . import auth, profile, wallet, games, webhooks

def setup_routes(app: web.Application):
    # Public API
    app.router.add_post("/api/auth", auth.api_auth)
    app.router.add_get("/api/currencies", wallet.api_currencies)
    app.router.add_get("/api/top-winnings", games.api_top_winnings)
    app.router.add_get("/api/solana-config", wallet.api_solana_config)
    
    # Webhooks
    app.router.add_post("/api/crypto-webhook", webhooks.api_crypto_webhook)
    app.router.add_post("/api/stars-webhook", webhooks.api_stars_webhook)
    
    # Auth Required (handled via middleware in create_app if we want, or decorated)
    # To keep it simple and match bot.py logic, we'll use wrappers if needed, 
    # but the instructions suggest a thin layer.
    
    # User Profile
    app.router.add_get("/api/balance", profile.api_balance)
    app.router.add_get("/api/profile", profile.api_profile)
    app.router.add_get("/api/notifications", profile.api_notifications)
    app.router.add_post("/api/notifications/read", profile.api_notifications_read)
    app.router.add_post("/api/set-currency", profile.api_set_currency)
    app.router.add_post("/api/set-language", profile.api_set_language)
    
    # Wallet & Payments
    app.router.add_get("/api/promos", wallet.api_promos)
    app.router.add_get("/api/bonuses", wallet.api_bonuses)
    app.router.add_get("/api/transactions", wallet.api_transactions)
    app.router.add_post("/api/create-deposit", wallet.api_create_deposit)
    app.router.add_post("/api/create-stars-invoice", wallet.api_create_stars_invoice)
    app.router.add_post("/api/create-invoice", wallet.api_create_crypto_invoice)
    app.router.add_post("/api/claim-bonus", wallet.api_claim_bonus)
    app.router.add_post("/api/activate-bonus", wallet.api_activate_bonus)
    app.router.add_post("/api/withdraw", wallet.api_withdraw)
    app.router.add_post("/api/solana-deposit", wallet.api_solana_deposit)
    app.router.add_post("/api/solana-nonce", wallet.api_solana_nonce)
    
    # Games
    app.router.add_post("/api/spin", games.api_spin)
    app.router.add_post("/api/bonus", games.api_bonus_spin)
    app.router.add_post("/api/wheel", games.api_wheel_spin)
    app.router.add_get("/api/wheel-status", games.api_wheel_status)
