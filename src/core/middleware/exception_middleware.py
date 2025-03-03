from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core.exceptions import AuthServiceError


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)

            return response
        except AuthServiceError as exc:
            if exc.status_code == 403:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"success": False, "message": exc.detail},
                )
