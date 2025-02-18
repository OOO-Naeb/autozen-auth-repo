from dataclasses import dataclass
from typing import Optional

from pydantic import EmailStr

from src.domain.interfaces.auth_dto_interfaces import IAuthResponseDTO
from src.domain.schemas import RolesEnum



@dataclass(frozen=True)
class RegisterResponseDTO(IAuthResponseDTO):
    """
    Domain schema for Register Response.
    Represents the data returned after successful user registration.
    """
    first_name: str
    last_name: str

    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    roles: list[RolesEnum] = None

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        base_dict = dict(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone_number=self.phone_number,
            roles=[role for role in self.roles],
        )

        return base_dict
