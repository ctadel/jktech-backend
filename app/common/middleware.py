import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.common.logger import access_logger


class AccessLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        client_ip = request.client.host
        method = request.method
        path = request.url.path
        status_code = response.status_code
        user_agent = request.headers.get("user-agent", "-")

        log_message = f'{client_ip} - "{method} {path}" {status_code} - {process_time:.2f}ms - {user_agent}'
        access_logger.info(log_message)

        return response
