from datetime import datetime, timedelta, timezone

import jwt

from src.core.config import settings
from src.domain.schemas import AccessToken, RefreshToken


class JWTService:
    def __init__(self):
        self.private_key = settings.jwt_private_secret_key
        self.algorithm = settings.jwt_algorithm

    async def generate_access_token(self, user_id: int, roles: dict, expire_time_in_minutes: int = settings.access_token_expire_time) -> AccessToken:
        payload = {
            'sub': user_id,
            'roles': roles,
            'token_type': 'access',
            'exp': datetime.now(timezone.utc) + timedelta(minutes=expire_time_in_minutes),
            'iat': datetime.now(timezone.utc)
        }

        return jwt.encode(payload, self.private_key, algorithm=settings.jwt_algorithm)

    async def generate_refresh_token(self, user_id: int, roles: dict, expire_time_in_days: int = settings.refresh_token_expire_time) -> RefreshToken:
        payload = {
            'sub': user_id,
            'roles': roles,
            'token_type': 'refresh',
            'exp': datetime.now(timezone.utc) + timedelta(days=expire_time_in_days),
            'iat': datetime.now(timezone.utc)
        }

        return jwt.encode(payload, self.private_key, algorithm=settings.jwt_algorithm)
