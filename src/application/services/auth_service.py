from typing import Annotated
from fastapi import Depends

from src.core.jwt_service import JWTService
from src.domain.exceptions import NotFoundException, UnauthorizedException
from src.domain.schemas import LoginRequestForm, Tokens, UserFromDB
from src.infrastructure.adapters.rabbitmq_user_adapter import RabbitMQUserAdapter
from src.infrastructure.interfaces.user_adapter_interface import IUserAdapter


class AuthService:
    def __init__(self, user_adapter: Annotated[IUserAdapter, Depends(RabbitMQUserAdapter)], jwt_service: Annotated[JWTService, Depends()]):
        self.user_adapter = user_adapter
        self.jwt_service = jwt_service

    async def login(self, data: LoginRequestForm) -> tuple[int, Tokens]:
        if data['email']:
            new_access_token = await self.jwt_service.generate_access_token(1, {
                'crs_admin': 'Car Service Station Administrator access.'})
            new_refresh_token = await self.jwt_service.generate_refresh_token(1, {
                'crs_admin': 'Car Service Station Administrator access.'})
            return 200, Tokens(access_token=new_access_token, refresh_token=new_refresh_token)

        elif data['phone_number']:
            user_from_db = await self.user_adapter.get_by_phone_number(data.phone_number)
            if not user_from_db:
                raise NotFoundException('There is no user with this phone number registered.')

            if user_from_db.password != data.password:
                raise UnauthorizedException('Credentials do not match. Phone number or password is incorrect.')

            new_access_token = self.jwt_service.generate_access_token(user_from_db.id, {
                'crs_admin': 'Car Service Station Administrator access.'})
            new_refresh_token = self.jwt_service.generate_refresh_token(user_from_db.id,
                                {'crs_admin': 'Car Service Station Administrator access.'})

            return 200, Tokens(access_token=new_access_token, refresh_token=new_refresh_token)

    async def refresh(self, refresh_token_payload: dict) -> tuple[int, Tokens]:
        print("PAYLOAD RECEIVED IN AuthService:", refresh_token_payload)
        new_access_token = await self.jwt_service.generate_access_token(refresh_token_payload['sub'], refresh_token_payload['roles'])
        new_refresh_token = await self.jwt_service.generate_refresh_token(refresh_token_payload['sub'], refresh_token_payload['roles'])

        return 200, Tokens(access_token=new_access_token, refresh_token=new_refresh_token)

    async def register(self, data: dict) -> tuple[int, UserFromDB]:
        return 201, UserFromDB(id=1, **data)
