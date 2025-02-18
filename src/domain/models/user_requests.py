from dataclasses import dataclass
import datetime

from src.domain.schemas import RolesEnum


@dataclass(frozen=True)
class AddUserRequestDTO:
    """
    Domain schema for Add User Request.
    Represents the data needed to add user to the DB in the domain logic.
    """
    first_name: str
    last_name: str
    hashed_password: str
    roles: list[RolesEnum]

    email: str
    phone_number: str

    is_active: bool = True

    created_at: datetime = datetime.datetime.now(datetime.UTC)
    updated_at: datetime = datetime.datetime.now(datetime.UTC)

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return {
            "email": self.email,
            "phone_number": self.phone_number,
            "hashed_password": self.hashed_password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "roles": [role for role in self.roles],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
