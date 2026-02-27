import hashlib
import hmac
import json
import logging
import bcrypt
import jwt as pyjwt
from datetime import datetime, timezone
from app.core import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def generate_jwt(payload: dict) -> str:
    return pyjwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_jwt(token: str) -> dict:
    return pyjwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])

def validate_telegram_data(init_data: str):
    if not settings.BOT_TOKEN:
        return False
    
    try:
        from urllib.parse import parse_qs, unquote
        parsed = {k: v[0] for k, v in parse_qs(init_data).items()}
        hash_val = parsed.pop('hash', '')
        
        # Check expiry (24h) if auth_date is present
        auth_date = int(parsed.get('auth_date', 0))
        if auth_date and (datetime.now().timestamp() - auth_date > 86400):
            logging.warning("Auth data expired")
            return False

        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(parsed.items())])
        secret_key = hmac.new("WebAppData".encode(), settings.BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if hmac.compare_digest(calculated_hash, hash_val):
            return parsed
        return None
    except Exception as e:
        logging.error(f"Telegram validation error: {e}")
        return None
