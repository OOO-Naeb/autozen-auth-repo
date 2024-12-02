from src.application.use_cases.auth_use_case import AuthUseCase
from src.domain.schemas import Tokens, LoginRequestForm, UserFromDB


async def login(data: LoginRequestForm, auth_use_case: AuthUseCase) -> tuple[int, Tokens]:
    return await auth_use_case.login(data)


async def refresh(refresh_token_payload: dict, auth_use_case: AuthUseCase) -> tuple[int, Tokens]:
    return await auth_use_case.refresh(refresh_token_payload)


async def register(data: dict, auth_use_case: AuthUseCase) -> tuple[int, UserFromDB]:
    return await auth_use_case.register(data)
