from abc import ABC, abstractmethod
from typing import Dict, Any

from src.domain.models.user_requests import AddUserRequestDTO
from src.domain.models.user_responses import UserAuthResponseDTO, UserResponseDTO
from src.domain.schemas import RabbitMQResponse


class IUserAdapter(ABC):
    @abstractmethod
    async def connect(self):
        """
        Establishes a connection to the RabbitMQ service and reinstates the channel if it's closed.

        Raises:
            RabbitMQError: When RabbitMQ service is not available.
        """
        pass

    async def _make_rpc_call(self, operation_type: str,
            payload: Dict[str, Any],
            timeout: int = 5):
        """
        Sends an RPC call through RabbitMQ to the User Service and waits for the response.

        Args:
            operation_type: Operation type to be called as handler-method in User Service.
            payload: Request body to send.
            timeout: Timeout for waiting for the response.

        Returns:
            RabbitMQResponse containing the User Service response.

        Raises:
            UserServiceError: When User Service is unavailable, not responding.
            RabbitMQError: When RabbitMQ is not available.
            AuthServiceError: For unexpected errors.
        """
        pass

    async def get_by_id(self, given_id: int, include_password_hash: bool) -> UserResponseDTO | UserAuthResponseDTO:
        """
        Retrieves a user by their ID from the User Service.

        Args:
            given_id: The ID of the user to retrieve.
            include_password_hash: Whether to include the hashed_password hash in the response or not.

        Returns:
            UserResponseDTO: Domain schema of the retrieved user WITHOUT hashed_password.
            OR
            UserAuthResponseDTO: Domain schema of the retrieved user WITH hashed_password.
        """
        pass

    async def get_by_phone_number(self, phone_number: str, include_password_hash: bool) -> UserResponseDTO | UserAuthResponseDTO:
        """
        Retrieves a user by their phone number from the User Service.

        Args:
            phone_number: The phone number of the user to retrieve.
            include_password_hash: Whether to include the hashed_password hash in the response or not.

        Returns:
            UserResponseDTO: Domain schema of the retrieved user WITHOUT hashed_password.
            OR
            UserAuthResponseDTO: Domain schema of the retrieved user WITH hashed_password.
        """
        pass

    async def get_by_email(self, email: str, include_password_hash: bool) -> UserResponseDTO | UserAuthResponseDTO:
        """
        Retrieves a user by their email from the User Service.

        Args:
            email: The email of the user to retrieve.
            include_password_hash: Whether to include the hashed_password hash in the response or not.

        Returns:
            UserResponseDTO: Domain schema of the retrieved user WITHOUT hashed_password.
            OR
            UserAuthResponseDTO: Domain schema of the retrieved user WITH hashed_password.
        """
        pass

    async def add(self, user_data: AddUserRequestDTO) -> UserResponseDTO:
        """
        Adds a new user to the DB through User Service.

        Args:
            user_data: User's data to add.

        Returns:
            UserResponseDTO: Domain schema of the retrieved user
        """
        pass

    def _handle_error_response(self, response: RabbitMQResponse):
        """
        Handles the error responses from the User Service.
        """
        pass