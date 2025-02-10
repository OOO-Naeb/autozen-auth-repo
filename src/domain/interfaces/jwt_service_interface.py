import uuid
from abc import abstractmethod, ABC

from src.core.config import settings
from src.domain.schemas import RolesEnum


class IJWTService(ABC):
    @abstractmethod
    def generate_access_token(self, user_id: uuid, roles: list[RolesEnum],
                                    expire_time_in_minutes: int = settings.access_token_expire_time) -> str:
        pass

    @abstractmethod
    def generate_refresh_token(self, user_id: uuid, roles: list[RolesEnum], expire_time_in_days: int = settings.refresh_token_expire_time) -> str:
        pass
