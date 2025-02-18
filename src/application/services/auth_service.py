from src.domain.interfaces.auth_service_interface import IAuthService


class AuthService(IAuthService):
    """Service for authentication (hashed_password verification)."""
    def __init__(self, password_hasher):
        self._password_hasher = password_hasher

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return self._password_hasher.verify(plain_password, password_hash)
