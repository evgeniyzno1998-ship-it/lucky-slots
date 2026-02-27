import logging
from datetime import datetime, timezone
from app.infrastructure.db.pool import db

def _now():
    return datetime.now(timezone.utc)

async def add_balance(uid: int, delta_cents: int, source_type: str, reference_id: str = "", req_id: str = None) -> dict:
    if delta_cents == 0:
        u = await db("SELECT balance_cents FROM users WHERE user_id=$1", (int(uid),), one=True, req_id=req_id)
        return {"ok": True, "balance_after": u['balance_cents'] if u else 0}

    async with db.transaction() as conn:
        u = await conn.fetchrow("SELECT balance_cents FROM users WHERE user_id=$1 FOR UPDATE", int(uid))
        if not u:
            return {"ok": False, "error": "user_not_found"}
            
        bal_before = u['balance_cents']
        bal_after = bal_before + delta_cents
        
        if bal_after < 0:
            return {"ok": False, "error": "insufficient_funds"}
        
        await conn.execute("UPDATE users SET balance_cents = $1 WHERE user_id=$2", bal_after, int(uid))
        await conn.execute(
            "INSERT INTO balance_ledger(user_id, source_type, amount_cents, balance_before, balance_after, reference_id, created_at) "
            "VALUES($1, $2, $3, $4, $5, $6, $7)",
            int(uid), source_type, delta_cents, bal_before, bal_after, str(reference_id), _now()
        )
        return {"ok": True, "balance_after": bal_after}

async def record_payment(uid, direction, amount_usd, amount_cents, method="crypto_bot", status="completed", invoice_id="", details="", oracle_source="crypto_bot", req_id=None):
    # This involves a join or separate fetch in the original, we'll keep it repo-specific
    u = await db("SELECT balance_cents FROM users WHERE user_id=$1", (int(uid),), one=True, req_id=req_id)
    bal_before = u['balance_cents'] if u else 0
    bal_after = bal_before + amount_cents if direction == "deposit" else bal_before - amount_cents
    
    await db(
        "INSERT INTO payments(user_id,direction,amount_usd,amount_cents,method,status,invoice_id,balance_before,balance_after,details,oracle_source,created_at) "
        "VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)",
        (int(uid), direction, amount_usd, amount_cents, method, status, invoice_id, bal_before, bal_after, details, oracle_source, _now()),
        req_id=req_id
    )
    
    if status == 'completed':
        if direction == "deposit":
            await db("UPDATE users SET total_deposited_usd=total_deposited_usd+$1 WHERE user_id=$2", (amount_usd, int(uid)), req_id=req_id)
        else:
            await db("UPDATE users SET total_withdrawn_usd=total_withdrawn_usd+$1 WHERE user_id=$2", (amount_usd, int(uid)), req_id=req_id)

async def get_payment_by_invoice(invoice_id: str, req_id: str = None):
    return await db("SELECT * FROM payments WHERE invoice_id=$1 LIMIT 1", (invoice_id,), one=True, req_id=req_id)

async def update_payment_status(invoice_id: str, status: str, req_id: str = None):
    await db("UPDATE payments SET status=$1, created_at=$2 WHERE invoice_id=$3", (status, _now(), invoice_id), req_id=req_id)

async def get_recent_payments(uid: int, limit: int = 20, req_id: str = None):
    return await db(
        "SELECT direction,amount_usd,amount_cents,method,status,created_at FROM payments "
        "WHERE user_id=$1 ORDER BY id DESC LIMIT $2",
        (int(uid), limit), fetch=True, req_id=req_id
    )
