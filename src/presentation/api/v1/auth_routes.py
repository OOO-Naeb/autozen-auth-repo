from starlette import status
from starlette.responses import JSONResponse

from src.application.use_cases.auth_use_case import AuthUseCase
from src.domain.schemas import Tokens, LoginRequestForm, RefreshToken, RegisterRequestForm


async def login(data: LoginRequestForm, auth_use_case: AuthUseCase) -> Tokens:
    return await auth_use_case.login(data)

async def refresh(refresh_token_payload: dict, auth_use_case: AuthUseCase) -> Tokens:
    return await auth_use_case.refresh(refresh_token_payload)

async def register(data: RegisterRequestForm, auth_use_case: AuthUseCase):
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User was registered successfully."})
