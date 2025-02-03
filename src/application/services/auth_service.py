from typing import Annotated
from fastapi import Depends

from src.application.services.jwt_service import JWTService
from src.domain.schemas import LoginRequestForm, Tokens, UserFromDB, RolesEnum
from src.infrastructure.adapters.rabbitmq_user_adapter import RabbitMQUserAdapter
from src.infrastructure.interfaces.user_adapter_interface import IUserAdapter


class AuthService:
    def __init__(self, user_adapter: Annotated[IUserAdapter, Depends(RabbitMQUserAdapter)], jwt_service: Annotated[JWTService, Depends()]):
        self.user_adapter = user_adapter
        self.jwt_service = jwt_service

    async def login(self, data: dict) -> tuple[int, Tokens] | None:
        data = LoginRequestForm(**data)

        if data.email:
            new_access_token = await self.jwt_service.generate_access_token(1, [
                RolesEnum.USER,
                RolesEnum.CSS_EMPLOYEE,
                RolesEnum.CSS_ADMIN
            ])
            new_refresh_token = await self.jwt_service.generate_refresh_token(1, [
                RolesEnum.USER,
                RolesEnum.CSS_EMPLOYEE,
                RolesEnum.CSS_ADMIN
            ])
            return 200, Tokens(access_token=str(new_access_token), refresh_token=str(new_refresh_token))

        elif data.phone_number:
            # Commented for DEV DEBUGGING only.

            # user_from_db = await self.user_adapter.get_by_phone_number(data.phone_number)
            # if not user_from_db:
            #     raise NotFoundException('There is no user with this phone number registered.')
            #
            # if user_from_db.password != data.password:
            #     raise UnauthorizedException('Credentials do not match. Phone number or password is incorrect.')

            new_access_token = await self.jwt_service.generate_access_token(1, [
                RolesEnum.USER,
                RolesEnum.CSS_EMPLOYEE,
                RolesEnum.CSS_ADMIN
            ])
            new_refresh_token = await self.jwt_service.generate_refresh_token(1, [
                RolesEnum.USER,
                RolesEnum.CSS_EMPLOYEE,
                RolesEnum.CSS_ADMIN
            ])

            return 200, Tokens(access_token=str(new_access_token), refresh_token=str(new_refresh_token))

    async def refresh(self, refresh_token_payload: dict) -> tuple[int, Tokens]:
        print("PAYLOAD RECEIVED IN AuthService:", refresh_token_payload)
        new_access_token = await self.jwt_service.generate_access_token(refresh_token_payload['sub'], refresh_token_payload['roles'])
        new_refresh_token = await self.jwt_service.generate_refresh_token(refresh_token_payload['sub'], refresh_token_payload['roles'])

        return 200, Tokens(access_token=str(new_access_token), refresh_token=str(new_refresh_token))

    async def register(self, data: dict) -> tuple[int, UserFromDB]:
        return 201, UserFromDB(id=1, **data)
