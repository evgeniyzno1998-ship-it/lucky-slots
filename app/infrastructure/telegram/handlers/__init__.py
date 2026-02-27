from aiohttp import web
from app.infrastructure.telegram import handlers

def setup_handlers(dp):
    # Register command handlers
    dp.message.register(handlers.cmd_start, handlers.Command("start"))
    
    # Register message handlers
    dp.message.register(handlers.handle_message)
    
    # Register callback query handlers
    dp.callback_query.register(handlers.handle_callback)
    
    # Register payment handlers
    dp.pre_checkout_query.register(handlers.process_pre_checkout)
    dp.message.register(handlers.process_successful_payment, handlers.F.successful_payment)
