import logging
import asyncpg
import time
import contextlib
from app.core import settings

class Database:
    def __init__(self):
        self.pool = None

    async def init(self):
        if not self.pool:
            logging.info("Initializing PostgreSQL pool...")
            self.pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=1,
                max_size=2,
                command_timeout=60.0
            )
        return self.pool

    async def __call__(self, q, p=(), fetch=False, one=False, conn=None, req_id=None):
        if not self.pool and not conn:
            logging.error(f"[DB_ERR] REQ_ID={req_id or 'N/A'} DB pool not initialized!")
            return None

        nq = q
        start = time.time()
        try:
            if conn:
                if fetch:
                    rows = await conn.fetch(nq, *p)
                    res = [dict(r) for r in rows] if rows else []
                elif one:
                    row = await conn.fetchrow(nq, *p)
                    res = dict(row) if row else None
                else:
                    await conn.execute(nq, *p)
                    res = None
            else:
                async with self.pool.acquire() as conn:
                    if fetch:
                        rows = await conn.fetch(nq, *p)
                        res = [dict(r) for r in rows] if rows else []
                    elif one:
                        row = await conn.fetchrow(nq, *p)
                        res = dict(row) if row else None
                    else:
                        await conn.execute(nq, *p)
                        res = None
            
            latency = (time.time() - start) * 1000
            if latency > 500:
                logging.warning(f"🐢 [SLOW_SQL] REQ_ID={req_id or 'N/A'} {latency:.2f}ms | {nq} | ARGS={len(p)}")
            
            return res
        except Exception as e:
            logging.error(f"❌ [DB_EXCEPTION] REQ_ID={req_id or 'N/A'} ERROR: {e} | SQL: {nq}")
            raise e

    @contextlib.asynccontextmanager
    async def transaction(self):
        if not self.pool:
            logging.error("DB pool not initialized for transaction!")
            raise RuntimeError("DB pool not initialized")
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def health_check(self, conn=None):
        logging.info("🩺 Running DB Health Check...")
        try:
            target = conn or self.pool
            # Check users table critical columns
            columns = await target.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('created_at', 'last_login', 'last_bot_interaction', 'last_activity')
            """)
            for col in columns:
                if col['data_type'] not in ('timestamp with time zone', 'text'):
                    logging.error(f"⚠️ SCHEMA MISMATCH: users.{col['column_name']} is {col['data_type']}")
                else:
                    logging.info(f"✅ users.{col['column_name']} is {col['data_type']}")
            
            res = await target.fetchval("SELECT 1")
            if res == 1:
                logging.info("✅ DB Connectivity: OK")
            return True
        except Exception as e:
            logging.error(f"❌ DB Health Check failed: {e}")
            return False

async def ensure_timestamp_column(conn, table: str, column: str):
    logging.info(f"🔎 Auditing {table}.{column}...")
    row = await conn.fetchrow("""
        SELECT data_type, column_default
        FROM information_schema.columns 
        WHERE table_name = $1 AND column_name = $2
    """, table, column)
    
    if not row:
        return

    current_type = row['data_type'].lower()
    col_default = row['column_default']
    
    if current_type == "timestamp with time zone":
        return

    if current_type in ["text", "character varying"]:
        await conn.execute(f"UPDATE {table} SET {column} = NULL WHERE {column} IS NOT NULL AND trim({column}) = ''")
        if col_default:
            await conn.execute(f"ALTER TABLE {table} ALTER COLUMN {column} DROP DEFAULT")
        await conn.execute(f"ALTER TABLE {table} ALTER COLUMN {column} TYPE TIMESTAMPTZ USING NULLIF(trim({column}), '')::TIMESTAMPTZ")
        await conn.execute(f"ALTER TABLE {table} ALTER COLUMN {column} SET DEFAULT NOW()")
    else:
        raise RuntimeError(f"Unexpected type {current_type} for {table}.{column}")

# Global instance for easy use
db = Database()
