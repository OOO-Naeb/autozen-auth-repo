import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union, List, Any, Dict
from uuid import UUID

from src.core.config import settings


@dataclass
class RabbitMQResponse:
    """Value object for RabbitMQ response with error handling."""
    status_code: int
    body: Union[str, dict]
    success: bool
    error_message: Optional[str] = None
    error_origin: Optional[str] = None

    @classmethod
    def success_response(cls, status_code: int, body: Union[str, dict]) -> "RabbitMQResponse":
        return cls(
            status_code=status_code,
            body=body,
            success=True
        )

    @classmethod
    def error_response(cls, status_code: int, message: str = '', error_origin: str = 'Auth Service') -> "RabbitMQResponse":
        return cls(
            status_code=status_code,
            body={},
            success=False,
            error_message=message,
            error_origin=error_origin
        )


class RolesEnum(str, Enum):
    CSS_EMPLOYEE = 'css_employee'
    CSS_ADMIN = 'css_admin'
    USER = 'user'


@dataclass(frozen=True)
class UserCredentials:
    password: str
    email: Optional[str] = None
    phone_number: Optional[str] = None

    def validate(self) -> None:
        if not (self.email or self.phone_number):
            raise ValueError("Either email or phone number must be provided.")
        if not self.password:
            raise ValueError("Password must be provided.")


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: str

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token
        }


@dataclass(frozen=True)
class RefreshTokenRequest:
    user_id: UUID
    roles: List[RolesEnum]

    created_at: datetime
    updated_at: datetime

    expire_time_in_days: int = settings.refresh_token_expire_time

    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        return dict(
            user_id=self.user_id,
            roles=[role.value for role in self.roles],
            created_at=self.created_at,
            updated_at=self.updated_at,
            expire_time_in_days=self.expire_time_in_days
        )

    def convert_datetime_fields_to_str(self, data: Any) -> Any:
        """ Convert datetime/date fields to strings in the given data. """
        if isinstance(data, (datetime, datetime.date)):
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
