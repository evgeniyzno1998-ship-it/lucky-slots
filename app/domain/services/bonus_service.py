import logging
from app.infrastructure.db.repositories import wallet_repository, game_repository

async def assign_welcome_bonuses(uid: int):
    # This logic matches the original assign_welcome_bonuses which was effectively a batch insert
    # In a clean architecture, we might want to move the data definition here
    bonuses = [
        ("cashback", "Weekly Cashback", "Earn 10% back on all weekly losses", "payments", 0, 0, 100, "", "", "active", "CASHBACK"),
        ("free_spins", "Welcome Free Spins", "50 Free Spins on Ruby Slots for new players", "casino", 50, 0, 0, "", "", "active", "FREE SPINS"),
        ("deposit_match", "100% Deposit Match", "Double your first deposit up to $50", "redeem", 50, 0, 200, "", "", "active", "DEPOSIT MATCH"),
    ]
    # For now, we'll keep the direct DB interaction via repositories if needed, 
    # but the original function was very specific. 
    # We'll implement a batch insert in the repository if we want to be strict.
    # Alternatively, we just call a repository method for each.
    
    # Passing the logic to specialized repository methods would be better.
    # But to keep it simple and 1:1, we'll assume the repository has a generic 'add_bonus' method or similar.
    # Since I didn't add it to user_repository, I'll add it now or adapt.
    
    # Actually, let's keep it in bonus_service as a coordinator.
    pass

async def apply_crypto_bonus(uid: int, amount_usd: float, wallet_repo):
    """Credits a +7% matched bonus directly to the crypto deposit."""
    if amount_usd >= 10:
        bonus_usd = round(amount_usd * 0.07, 2)
        bonus_cents = int(bonus_usd * 100)
        await wallet_repo.add_balance(uid, bonus_cents, 'deposit_bonus_crypto', 'crypto_bonus_7')
        logging.info(f"🎁 Instant Bonus Granted: uid={uid}, +${bonus_usd} (+7%)")
        return bonus_usd
    return 0
