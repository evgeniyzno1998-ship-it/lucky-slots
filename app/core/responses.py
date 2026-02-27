from aiohttp import web
import logging
import json
from app.core import security

def json_ok(data: dict = None, message: str = None, req_id: str = None):
    payload = {"ok": True}
    if data:
        payload.update(data)
    if message:
        payload["message"] = message
    if req_id:
        payload["req_id"] = req_id
    return web.json_response(payload)

def json_err(code: str, message: str = None, status: int = 400, req_id: str = None):
    logging.warning(f"⚠️ [API_ERR] REQ_ID={req_id or 'N/A'} {code}: {message or ''}")
    body = {
        "ok": False,
        "data": {},
        "error": {
            "code": code,
            "message": message or ""
        }
    }
    if req_id: body["error"]["req_id"] = req_id
    return web.json_response(body, status=status)
