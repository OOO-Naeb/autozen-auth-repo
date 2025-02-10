class AuthenticationError(Exception):
    """Base class for authentication related errors."""
    def __init__(self, message: str, status_code: int = 401):
        self.status_code = status_code
        super().__init__(message)

class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid."""
    def __init__(self, message: str = "Invalid credentials provided."):
        super().__init__(message=message, status_code=401)

class UserNotFoundError(AuthenticationError):
    """Raised when user is not found."""
    def __init__(self, message: str = "User not found."):
        super().__init__(message=message, status_code=404)

class InactiveUserError(AuthenticationError):
    """Raised when user account is inactive."""
    def __init__(self, message: str = "User account is inactive."):
        super().__init__(message=message, status_code=403)

class InvalidPasswordError(AuthenticationError):
    """Raised when password verification fails."""
    def __init__(self, message: str = "Invalid password."):
        super().__init__(message=message, status_code=401)

class TokenGenerationError(AuthenticationError):
    """Raised when token generation fails."""
    def __init__(self, message: str = "Failed to generate authentication tokens."):
        super().__init__(message=message, status_code=500)
