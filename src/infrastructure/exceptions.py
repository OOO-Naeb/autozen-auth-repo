from src.core.exceptions import AuthServiceError


class RabbitMQError(AuthServiceError):
    """Exception for RabbitMQ connection errors."""
    def __init__(self, detail: str = "An error occurred in RabbitMQ.", status_code: int = 503):
        super().__init__(detail=detail, status_code=status_code)


class UserServiceError(AuthServiceError):
    """Exception for User Service's responses errors."""
    def __init__(self, detail: str = "An error occurred in the User Service.", status_code: int = 500):
        super().__init__(detail=detail, status_code=status_code)
