import logging
from aiogram import Bot, Dispatcher
from app.core import settings
from app.infrastructure.telegram import handlers

async def create_bot():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Register handlers
    handlers.setup_handlers(dp)
    
    return bot, dp
