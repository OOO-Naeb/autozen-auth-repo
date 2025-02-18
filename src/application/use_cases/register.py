from src.core.logger import LoggerService
from src.domain.interfaces.password_hasher_interface import IPasswordHasher
from src.domain.interfaces.user_adapter_interface import IUserAdapter
from src.domain.models.user_requests import AddUserRequestDTO
from src.domain.models.user_responses import UserResponseDTO


class RegisterUseCase:
    """
    USE CASE: Register a user and return their data.
    """

    def __init__(
            self,
            user_adapter: IUserAdapter,
            password_hasher: IPasswordHasher,
            logger: LoggerService
    ):
        self._user_adapter = user_adapter
        self._password_hasher = password_hasher
        self._logger = logger

    async def execute(self, user_data: dict) -> UserResponseDTO:
        """
        Executes the register flow:
        1. Map the user data to a dictionary.
        2. Replace the plain password with a hashed password.
        3. Map the dictionary to an AddUserRequestDTO object.
        4. Call for an adapter method to add the user.

        Args:
            user_data (dict): User's data to register.

        Returns:
            UserResponseDTO: created user's data.
        """
        plain_password = user_data.pop('password')
        hashed_password = self._password_hasher.hash(plain_password)

        user_data['hashed_password'] = hashed_password

        add_user_request = AddUserRequestDTO(**user_data)

        return await self._user_adapter.add(add_user_request)
