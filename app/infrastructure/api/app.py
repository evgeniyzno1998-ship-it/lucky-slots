from . import middleware, routes

async def create_app(db_pool):
    app = web.Application(middlewares=[
        middleware.global_middleware,
        middleware.auth_middleware
    ])
    app['db'] = db_pool
    
    # Register routes
    routes.setup_routes(app)
    
    return app

