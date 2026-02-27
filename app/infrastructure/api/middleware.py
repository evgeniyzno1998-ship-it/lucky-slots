import logging
import time
import uuid
from aiohttp import web
from app.core import security
from app.core.responses import json_err

@web.middleware
async def global_middleware(req, handler):
    req_id = str(uuid.uuid4())
    req['req_id'] = req_id
    start = time.time()
    
    try:
        res = await handler(req)
        latency = (time.time() - start) * 1000
        logging.info(f"🌐 [API] {req.method} {req.path} | {res.status} | {latency:.2f}ms | REQ_ID={req_id}")
        return res
    except web.HTTPException as e:
        return json_err("http_error", message=str(e), status=e.status, req_id=req_id)
    except Exception as e:
        logging.error(f"❌ [API_FATAL] REQ_ID={req_id} {e}", exc_info=True)
        return json_err("server_error", message="Internal server error", status=500, req_id=req_id)

@web.middleware
async def auth_middleware(req, handler):
    if req.path.startswith("/api/"):
        # Public routes
        if req.path in ["/api/auth", "/api/currencies", "/api/health", "/api/solana-config"]:
            return await handler(req)
        
        # Webhooks (ideally IP restricted or secret token)
        if "webhook" in req.path:
            return await handler(req)
            
        # Auth required routes
        auth_header = req.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = security.decode_jwt(token)
            if payload and payload.get("role") == "user":
                req['uid'] = int(payload.get("uid") or payload.get("sub"))
                return await handler(req)
        
        return json_err("unauthorized", status=401, req_id=req.get('req_id'))
        
    return await handler(req)
