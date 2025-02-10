import datetime
import uuid
from typing import Optional

from src.application.exceptions import InvalidCredentialsError, UserNotFoundError, InactiveUserError, \
    TokenGenerationError, InvalidPasswordError
from src.core.logger import LoggerService
from src.domain.interfaces.auth_service_interface import IAuthService
from src.domain.interfaces.jwt_service_interface import IJWTService
from src.domain.interfaces.user_adapter_interface import IUserAdapter
from src.domain.models.user import User
from src.domain.schemas import UserCredentials, AuthTokens, RolesEnum
from src.infrastructure.exceptions import UserServiceError, RabbitMQError, AuthServiceError


class LoginUseCase:
    """
    USE CASE: Login a user and generate JWT tokens for authentication.

    This use case handles the authentication flow:
    1. Validates user credentials
    2. Retrieves user data
    3. Verifies user status and password
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

    async def execute(self, credentials: UserCredentials) -> AuthTokens:
        """
        Executes the login flow.

        Args:
            credentials: User credentials containing email/phone and password

        Returns:
            AuthTokens containing access and refresh tokens

        Raises:
            InvalidCredentialsError: When credentials validation fails
            UserNotFoundError: When user is not found
            InactiveUserError: When user account is inactive
            InvalidPasswordError: When password verification fails
            TokenGenerationError: When token generation fails
        """
        try:
            # Validate credentials format
            if not credentials.validate():
                raise InvalidCredentialsError("Invalid credentials format.")

            # Get user
            user = await self._get_user(credentials)
            if not user:
                raise UserNotFoundError()

            # Validate user status
            if not user.if_active():
                raise InactiveUserError()

            # Verify password
            if not self._auth_service.verify_password(
                    credentials.password,
                    user.hashed_password
            ):
                self._logger.warning(f"Invalid password attempt for user: {user.id}")
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
            except Exception as e:
                self._logger.critical(f"Token generation failed. From LoginUseCase, execute(): {str(e)}")
                raise TokenGenerationError()

            return AuthTokens(
                access_token=str(access_token),
                refresh_token=str(refresh_token)
            )

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
                f"User identifier: {credentials.email or credentials.phone_number}"
            )
            raise

        except Exception as e:
            self._logger.critical(f"Unexpected error during authentication. From: LoginUseCase, execute(): {str(e)}")
            raise TokenGenerationError("Authentication failed due to internal error.")

    async def _get_user(self, credentials: UserCredentials) -> Optional[User]:
        """
        Retrieves user by email or phone number.

        Args:
            credentials: User credentials containing email or phone number

        Returns:
            User if found, None otherwise

        Raises:
            UserServiceError: When user service is unavailable
        """
        try:
            if credentials.email:
                return await self._user_adapter.get_by_email(credentials.email)

            return await self._user_adapter.get_by_phone_number(credentials.phone_number)
        except Exception as e:
            self._logger.error(f"Unexpected error while retrieving user. From: LoginUseCase, _get_user(): {str(e)}")
            raise UserNotFoundError()



# FOR TESTING PURPOSES ONLY
class StubLoginUseCase(LoginUseCase):
    """
    Stub-use case for testing purposes.
    """

    async def execute(self, credentials: UserCredentials) -> AuthTokens:
        # Create a fake user with all roles
        fake_user = User(
            id=uuid.uuid4(),
            email=credentials.email,
            phone_number=credentials.phone_number,
            hashed_password="stub_hashed_password",  # Stubbed hashed password
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