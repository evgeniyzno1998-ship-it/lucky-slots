import os
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

# Server
BOT_TOKEN = os.getenv("BOT_TOKEN")
CRYPTO_TOKEN = os.getenv("CRYPTO_TOKEN")
PORT = int(os.getenv("PORT", 8080))
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://lucky-slots-production.up.railway.app")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://evgeniyzno1998-ship-it.github.io/lucky-slots/")

# Security
JWT_SECRET = os.getenv("JWT_SECRET", BOT_TOKEN[:32] if BOT_TOKEN else "change-me-in-production")
JWT_EXPIRY_HOURS = 12
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "rubybet2024")

# Database
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres.xlkjdtfnqzmrblaomfrp:pOy8CePzLBKgNMvB@aws-1-eu-central-1.pooler.supabase.com:5432/postgres")

# Solana
SOLANA_TREASURY_PUBKEY = os.getenv("SOLANA_TREASURY_PUBKEY", "11111111111111111111111111111111")

# Domain Defaults
REFERRAL_BONUS = 10
