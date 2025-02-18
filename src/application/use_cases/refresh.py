from src.application.exceptions import TokenGenerationError
from src.core.logger import LoggerService
from src.domain.interfaces.jwt_service_interface import IJWTService
from src.domain.models.auth_requests import RefreshTokenRequestDTO
from src.domain.schemas import AuthTokens, RefreshTokenRequest


class RefreshUseCase:
    """
    USE CASE: Refresh the access token using the refresh token.
    """
    def __init__(
            self,
            jwt_service: IJWTService,
            logger: LoggerService
    ):
        self._jwt_service = jwt_service
        self._logger = logger

    async def execute(self, refresh_token_payload: dict) -> AuthTokens:
        """
        Executes the refresh flow.

        Args:
            refresh_token_payload (dict): Refresh token payload.

        Returns:
            AuthTokens domain model containing access and refresh tokens.

        Raises:
            TokenGenerationError: When token generation fails.
        """
        try:
            domain_schema_data = RefreshTokenRequestDTO(user_id=refresh_token_payload.get('user_id'), roles=refresh_token_payload.get('roles'))

            new_access_token = self._jwt_service.generate_refresh_token(
                user_id=domain_schema_data.user_id,
                roles=domain_schema_data.roles,
            )
            new_refresh_token = self._jwt_service.generate_refresh_token(
                user_id=domain_schema_data.user_id,
                roles=domain_schema_data.roles,
            )

            return AuthTokens(
                access_token=str(new_access_token),
                refresh_token=str(new_refresh_token)
            )
        except Exception as e:
            self._logger.critical(f"Token generation failed. From RefreshUseCase, execute(): {str(e)}")
            raise TokenGenerationError()
