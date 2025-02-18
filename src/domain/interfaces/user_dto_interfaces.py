from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.schemas import RolesEnum


@dataclass(frozen=True)
class IUserResponseDTO(ABC):
    """
    Abstract base class for all user responses domain schemas.
    Defines common attributes and methods for user responses.
    """
    id: UUID
    first_name: str
    last_name: str
    roles: list[RolesEnum]
    is_active: bool

    email: str
    phone_number: str

    created_at: datetime
    updated_at: datetime

    def is_user_active(self) -> bool:
        """Checks if the user is active."""
        return self.is_active

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        pass