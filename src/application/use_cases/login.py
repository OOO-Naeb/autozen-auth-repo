import datetime
import uuid
from typing import Optional

from src.application.exceptions import InvalidCredentialsError, UserNotFoundError, InactiveUserError, \
    TokenGenerationError, InvalidPasswordError
from src.core.logger import LoggerService
from src.domain.interfaces.auth_service_interface import IAuthService
from src.domain.interfaces.jwt_service_interface import IJWTService
from src.domain.interfaces.user_adapter_interface import IUserAdapter
from src.domain.models.auth_requests import LoginRequestDTO
from src.domain.models.user_responses import UserAuthResponseDTO
from src.domain.schemas import AuthTokens, RolesEnum
from src.infrastructure.exceptions import UserServiceError, RabbitMQError
from src.core.exceptions import AuthServiceError


class LoginUseCase:
    """
    USE CASE: Login a user and generate JWT tokens for authentication.

    This use case handles the authentication flow:
    1. Validates user credentials
    2. Retrieves user data
    3. Verifies user status and hashed_password
    4. Generates access and refresh tokens
    """

    def __init__(
            self,
            user_adapter: IUserAdapter,
            jwt_service: IJWTService,
            auth_service: IAuthService,
            logger: LoggerService
    ):
        self._user_adapter = user_adapter
        self._jwt_service = jwt_service
        self._auth_service = auth_service
        self._logger = logger

    async def execute(self, credentials: dict) -> AuthTokens:
        """
        Executes the login flow.

        Args:
            credentials: User credentials containing email/phone and hashed_password

        Returns:
            AuthTokens containing access and refresh tokens

        Raises:
            InvalidCredentialsError: When credentials validation fails
            UserNotFoundError: When user is not found
            InactiveUserError: When user account is inactive
            InvalidPasswordError: When hashed_password verification fails
            TokenGenerationError: When token generation fails
        """
        try:
            domain_schema_data = LoginRequestDTO(**credentials)
            # Validate credentials format
            if not domain_schema_data.is_valid():
                raise InvalidCredentialsError("Invalid credentials format.")

            # Get user
            user = await self._get_user(domain_schema_data)
            if not user:
                raise UserNotFoundError()

            # Validate user status
            if not user.is_user_active():
                raise InactiveUserError()

            # Verify hashed_password
            if not self._auth_service.verify_password(
                    domain_schema_data.password,
                    user.hashed_password
            ):
                self._logger.warning(f"Invalid hashed_password attempt for user: {user.id}")
                raise InvalidPasswordError()

            # Generate tokens
            try:
                access_token = self._jwt_service.generate_access_token(
                    user_id=user.id,
                    roles=user.roles
                )
                refresh_token = self._jwt_service.generate_refresh_token(
                    user_id=user.id,
                    roles=user.roles
                )

                return AuthTokens(
                    access_token=str(access_token),
                    refresh_token=str(refresh_token)
                )
            except Exception as e:
                self._logger.critical(f"Token generation failed. From LoginUseCase, execute(): {str(e)}")
                raise TokenGenerationError()

        except (
                InvalidCredentialsError,
                UserNotFoundError,
                InactiveUserError,
                InvalidPasswordError,
                TokenGenerationError,
                UserServiceError,
                RabbitMQError,
                AuthServiceError
        ) as e:
            self._logger.info(
                f"Authentication failed: {str(e)}. "
                f"User identifier: {credentials.get('email') or credentials.get('phone_number')}"
            )
            raise
        except Exception as e:
            self._logger.critical(f"Unexpected error during authentication. From: LoginUseCase, execute(): {str(e)}")
            raise TokenGenerationError("Authentication failed due to internal error.")

    async def _get_user(self, credentials: LoginRequestDTO) -> Optional[UserAuthResponseDTO]:
        """
        Retrieves user by email or phone number.

        Args:
            credentials: User credentials containing email or phone number

        Returns:
            User if found, None otherwise
        """
        if credentials.email:
            return await self._user_adapter.get_by_email(credentials.email, include_password_hash=True)

        return await self._user_adapter.get_by_phone_number(credentials.phone_number, include_password_hash=True)



# FOR TESTING PURPOSES ONLY
class StubLoginUseCase(LoginUseCase):
    """
    Stub-use case for testing purposes.
    """

    async def execute(self, credentials: dict) -> AuthTokens:
        # Create a fake user with all roles
        domain_schema_data = LoginRequestDTO(**credentials)

        fake_user = UserAuthResponseDTO(
            id=uuid.uuid4(),
            email=domain_schema_data.email,
            phone_number=domain_schema_data.phone_number,
            hashed_password="stub_hashed_password",
            first_name="Fake",
            last_name="User",
            is_active=True,
            created_at=datetime.datetime.now(datetime.UTC),
            updated_at=datetime.datetime.now(datetime.UTC),
            roles=[
                RolesEnum.USER,
                RolesEnum.CSS_EMPLOYEE,
                RolesEnum.CSS_ADMIN
            ]
        )

        access_token = self._jwt_service.generate_access_token(
            user_id=fake_user.id,
            roles=fake_user.roles
        )
        refresh_token = self._jwt_service.generate_refresh_token(
            user_id=fake_user.id,
            roles=fake_user.roles
        )

        return AuthTokens(
            access_token=str(access_token),
            refresh_token=str(refresh_token)
        )