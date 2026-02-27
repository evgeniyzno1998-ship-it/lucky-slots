import asyncio
import logging
import signal
import os
import sys
import uuid
from aiohttp import web
from app.core import settings, logging as core_logging
from app.infrastructure.db.pool import db
from app.infrastructure.api.app import create_app
from app.infrastructure.telegram.bot import create_bot

POLLING_LOCK_ID = 8542792670

class PostgresPollingLock:
    def __init__(self, pool):
        self.pool = pool
        self.conn = None
        self.active = False
    async def acquire(self) -> bool:
        if not self.pool: return False
        try:
            if not self.conn: self.conn = await self.pool.acquire()
            locked = await self.conn.fetchval("SELECT pg_try_advisory_lock($1)", POLLING_LOCK_ID)
            self.active = bool(locked)
            return self.active
        except Exception as e:
            logging.error(f"[LOCK] Failed to acquire lock: {e}"); return False
    async def release(self):
        if self.conn:
            try:
                if self.active: await self.conn.execute("SELECT pg_advisory_unlock($1)", POLLING_LOCK_ID)
                await self.pool.release(self.conn)
            except: pass
            finally: self.conn = None; self.active = False

async def main():
    core_logging.setup_logging()
    await db.init()
    await db.health_check()
    
    bot, dp = await create_bot()
    app = await create_app(db.pool)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', settings.PORT)
    await site.start()
    
    instance_id = str(uuid.uuid4())[:8]
    lock = PostgresPollingLock(db.pool)
    stop_event = asyncio.Event()
    
    logging.info(f"🚀 Modular Monolith [{instance_id}] starting on port {settings.PORT}")
    
    while not stop_event.is_set():
        if await lock.acquire():
            logging.info(f"👑 Instance [{instance_id}] acquired Polling Lock.")
            try:
                await dp.start_polling(bot)
            except Exception as e:
                logging.error(f"❌ Polling Error: {e}")
            finally:
                await lock.release()
        else:
            logging.info(f"⏳ Instance [{instance_id}] - Polling occupied. Retrying...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit): pass
    except Exception as e: logging.fatal(f"FATAL: {e}", exc_info=True)
