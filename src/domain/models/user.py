from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Any, Dict
from uuid import UUID

from pydantic import EmailStr

from src.domain.schemas import RolesEnum


@dataclass
class User:
    hashed_password: str
    first_name: str
    last_name: str

    is_active: bool
    created_at: datetime.date
    updated_at: datetime.date
    roles: list[RolesEnum]

    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    id: Optional[UUID] = None

    def if_active(self) -> bool:
        """ Check if the user is active. """
        return self.is_active

    def to_dict(self) -> dict:
        """ Convert the domain object to a dictionary. """
        return {
            "id": self.id,
            "email": self.email,
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.if_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "roles": [role.value for role in self.roles],
        }

    def convert_datetime_fields_to_str(self, data: Any) -> Any:
        """ Convert datetime/date fields to strings in the given data. """
        if isinstance(data, (datetime, date)):
            return data.isoformat()
        elif isinstance(data, dict):
            return {key: self.convert_datetime_fields_to_str(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convert_datetime_fields_to_str(item) for item in data]
        else:
            return data

    def to_serializable_dict(self) -> Dict[str, Any]:
        """
        Convert the domain object to a dictionary with datetime/date fields converted to strings.
        """
        raw_dict = self.to_dict()

        return self.convert_datetime_fields_to_str(raw_dict)
