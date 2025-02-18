from dataclasses import dataclass, fields
from datetime import datetime
from uuid import UUID

from src.domain.interfaces.user_dto_interfaces import IUserResponseDTO
from src.domain.schemas import RolesEnum


@dataclass(frozen=True)
class UserResponseDTO(IUserResponseDTO):
    """
    Domain schema for User Service response.
    Represents the data received when we request for a User from User Service.

    DOES NOT include the hashed_password hash.
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

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "roles": [role.value for role in self.roles],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def do_not_include_password(cls, data: dict) -> "UserResponseDTO":
        """
        Create a UserResponseDTO object from a dictionary and IGNORES
        the provided hashed_password hash.

        ALWAYS USE when you create a UserResponseDTO object from a dictionary,
        because User Service sends the hashed_password hash in the response BY DEFAULT.
        """
        del data['hashed_password']
        return cls(**data)



@dataclass(frozen=True)
class UserAuthResponseDTO(IUserResponseDTO):
    """
    Domain schema for User Service response.
    Represents the data received when we request for a User from User Service.

    INCLUDES the hashed_password hash.
    FOR INTERNAL (SERVER SIDE) ONLY.
    """
    id: UUID
    first_name: str
    last_name: str
    hashed_password: str
    roles: list[RolesEnum]
    is_active: bool

    email: str
    phone_number: str

    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "phone_number": self.phone_number,
            "hashed_password": self.hashed_password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "roles": [role.value for role in self.roles],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
