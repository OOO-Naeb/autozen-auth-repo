from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.domain.interfaces.auth_dto_interfaces import IAuthRequestDTO
from src.domain.schemas import RolesEnum


@dataclass(frozen=True)
class LoginRequestDTO(IAuthRequestDTO):
    """
    Domain schema for Login Request.
    Represents the data needed to perform user login in the domain logic.
    """
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str = ""

    def is_valid(self) -> bool:
        """
        Checks if either email or phone number is provided.
        """
        return bool(self.email or self.phone_number) # Mimics the Pydantic validator logic

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return {
            "email": self.email,
            "phone_number": self.phone_number,
            "hashed_password": self.password
        }


@dataclass(frozen=True)
class RegisterRequestDTO(IAuthRequestDTO):
    """
    Domain schema for Register Request.
    Represents the data needed to register a new user in the domain logic.
    """
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str = ""
    first_name: str = ""
    last_name: str = ""
    roles: list[RolesEnum] = RolesEnum.USER

    def is_valid(self) -> bool:
        """
        Checks if either email or phone number is provided (non-empty).
        """
        return bool(self.email or self.phone_number)

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return {
            "email": self.email,
            "phone_number": self.phone_number,
            "hashed_password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "roles": [role for role in self.roles]
        }


@dataclass(frozen=True)
class RefreshTokenRequestDTO(IAuthRequestDTO):
    """
    Domain schema for Refresh Token Request.
    Represents the data needed to refresh user's authentication tokens in the domain logic.
    """
    user_id: UUID
    roles: list[RolesEnum]

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return {
            "user_id": self.user_id,
            "roles": [role for role in list(self.roles)]
        }
