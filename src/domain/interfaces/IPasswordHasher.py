from abc import abstractmethod, ABC


class IPasswordHasher(ABC):
    """Interface for password hashing operations."""

    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool:
        """Verifies if the plain password matches the hash."""
        pass

    @abstractmethod
    def hash(self, password: str) -> str:
        """Creates a hash from the password."""
        pass
