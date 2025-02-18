from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class IAuthResponseDTO(ABC):
    """
    Abstract base class for all authentication responses domain schemas.
    Defines common attributes and methods for auth responses.
    """
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        pass


class IAuthRequestDTO(ABC):
    """
    Abstract base class for all authentication requests domain schemas.
    Defines common interface for all auth requests.
    """
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the domain object to a dictionary."""
        pass
