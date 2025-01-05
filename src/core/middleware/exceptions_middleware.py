from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.domain.exceptions import UnauthorizedException, AccessDeniedException, NotFoundException, ConflictException, \
    SourceUnavailableException, SourceTimeoutException


class AuthExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response

        except UnauthorizedException as exc:
            return JSONResponse(
                status_code=401,
                content={"success": False, "message": exc.get_default_detail()},
            )
        except AccessDeniedException as exc:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": exc.get_default_detail()},
            )
        except NotFoundException as exc:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": exc.get_default_detail()},
            )
        except ConflictException as exc:
            return JSONResponse(
                status_code=409,
                content={"success": False, "message": exc.get_default_detail()},
            )
        except SourceUnavailableException as exc:
            return JSONResponse(
                status_code=503,
                content={"success": False, "message": exc.get_default_detail()},
            )
        except SourceTimeoutException as exc:
            return JSONResponse(
                status_code=504,
                content={"success": False, "message": exc.get_default_detail()},
            )
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"success": False, "message": exc.detail},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": "An unexpected error occurred. Please contact support."},
            )
