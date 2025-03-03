from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.core.exceptions import AuthServiceError

ALLOWED_IPS = ('localhost', '127.0.0.1')
# ALLOWED_PORTS = (8000, 8001, 56182)

class IPFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        # client_port = request.client.port

        if client_ip != "127.0.0.1":
            raise AuthServiceError(
                status_code=403,
                detail="Access denied: your IP is not allowed."
            )

        # if client_ip not in ALLOWED_IPS or client_port not in ALLOWED_PORTS:
        #     raise PaymentServiceError(
        #         status_code=403,
        #         detail="Access denied: your IP and port are not allowed."
        #     )

        return await call_next(request)
