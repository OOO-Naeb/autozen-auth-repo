import uuid
from datetime import datetime, timedelta, timezone

import jwt

from src.core.config import settings
from src.domain.interfaces.jwt_service_interface import IJWTService
from src.domain.schemas import RolesEnum


class JWTService(IJWTService):
    def __init__(self):
        self.private_key = settings.jwt_private_secret_key
        self.algorithm = settings.jwt_algorithm

    async def generate_access_token(self, user_id: uuid, roles: list[RolesEnum],
                                    expire_time_in_minutes: int = settings.access_token_expire_time) -> str:
        payload = {
            'sub': str(user_id),
            'roles': [role.value for role in roles],
            'token_type': 'access',
            'exp': datetime.now(timezone.utc) + timedelta(minutes=expire_time_in_minutes),
            'iat': datetime.now(timezone.utc)
        }

        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    async def generate_refresh_token(self, user_id: uuid, roles: list[RolesEnum], expire_time_in_days: int = settings.refresh_token_expire_time) -> str:
        payload = {
            'sub': str(user_id),
            'roles': [role.value for role in roles],
            'token_type': 'refresh',
            'exp': datetime.now(timezone.utc) + timedelta(days=expire_time_in_days),
            'iat': datetime.now(timezone.utc)
        }

        return jwt.encode(payload, self.private_key, algorithm=settings.jwt_algorithm)
