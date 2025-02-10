class AuthServiceError(Exception):
    """Base infrastructure exception for Auth Service errors."""
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)


class RabbitMQError(AuthServiceError):
    """Exception for RabbitMQ connection errors."""
    def __init__(self, detail: str = "An error occurred in RabbitMQ.", status_code: int = 503):
        super().__init__(detail=detail, status_code=status_code)


class UserServiceError(AuthServiceError):
    """Exception for User Service responses' errors."""
    def __init__(self, detail: str = "An error occurred in the User Service.", status_code: int = 500):
        super().__init__(detail=detail, status_code=status_code)
