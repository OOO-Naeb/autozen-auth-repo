from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

@dataclass
class RabbitMQResponse:
    """Value object for RabbitMQ response with error handling."""
    status_code: int
    body: Union[str, dict]
    success: bool = True
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
