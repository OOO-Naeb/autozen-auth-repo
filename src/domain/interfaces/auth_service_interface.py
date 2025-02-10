from abc import ABC, abstractmethod


class IAuthService(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        pass
