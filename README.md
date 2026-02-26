# RubyBet — Telegram Mini App (Solana & Casino)

A production-grade Telegram Mini App featuring a high-performance slots engine, Solana wallet integration, and a hardened Python backend.

## 🚀 Architecture
- **Frontend**: Vanilla JS + Tailwind CSS (Optimized for Telegram WebApp environment).
- **Backend**: Python 3.10+ (aiohttp + asyncpg) for high-concurrency RPC.
- **Database**: PostgreSQL (Hardened with native positional parameters and pooling).
- **Security**: HMAC-SHA256 Telegram validation, short-lived JWTs, and `withGuard` race condition protection.

## ⚙️ Environment Variables
The following environment variables are required:
- `BOT_TOKEN`: Your Telegram Bot Token.
- `JWT_SECRET`: High-entropy secret for session signing.
- `DATABASE_URL`: Connection string for PostgreSQL.
- `CRYPTO_TOKEN`: (Optional) CryptoBot API token for USDT payments.
- `PUBLIC_URL`: Public URL of your backend.

## 🛠 Local Development
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the variables listed above.
4. Run the backend:
   ```bash
   python bot.py
   ```

## 🚢 Deployment (Railway)
1. Link your GitHub repository to Railway.
2. Ensure the `DATABASE_URL` is set in Railway static variables.
3. The included `railway.json` and `Procfile` will handle building and starting the service automatically via Nixpacks.

## 🔒 Security & Stability Notes
- **Rate Limiting**: Integrated per-IP throttling on all `/api/` endpoints.
- **X-Request-Id**: Every request is correlated with a unique ID for observability.
- **Hardened RPC**: `apiFetch` includes silent re-auth, 10s timeouts, and safe JSON parsing.
