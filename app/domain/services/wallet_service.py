from app import config

def usdt_cents_to_display(cents: int, currency: str = 'USD') -> float:
    usd = cents / 100.0
    rate = config.CURRENCY_RATES.get(currency, 1.0)
    return round(usd * rate, 2)

def display_to_usdt_cents(amount: float, currency: str = 'USD') -> int:
    rate = config.CURRENCY_RATES.get(currency, 1.0)
    usd = amount / rate
    return int(round(usd * 100))
