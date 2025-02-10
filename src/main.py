import uvicorn
from fastapi import FastAPI
import asyncio

from src.application.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.application.services.auth_service import AuthService
from src.application.services.jwt_service import JWTService
from src.application.use_cases.login import LoginUseCase, StubLoginUseCase
from src.core.logger import LoggerService
from src.infrastructure.adapters.rabbitmq_api_gateway_listener import RabbitMQApiGatewayListener
from src.infrastructure.adapters.rabbitmq_user_adapter import RabbitMQUserAdapter


async def setup_dependencies():
    """
    Initialize all dependencies.

    This function creates and wires together all the components of our application:
    - Loggers for different services
    - Password hasher for secure password verification
    - Auth service for authentication operations
    - JWT service for token management
    - User adapter for communication with User Service
    - Login use case that orchestrates the authentication flow
    - RabbitMQ listener that handles incoming requests
    """
    # Initialize loggers for different components
    api_gateway_logger = LoggerService(__name__, "api_gateway_log.log")
    user_service_logger = LoggerService(__name__, "user_service_log.log")
    auth_service_logger = LoggerService(__name__, "auth_service_log.log")

    # Create core services
    jwt_service = JWTService()
    password_hasher = BcryptPasswordHasher()
    auth_service = AuthService(password_hasher=password_hasher)

    # Create data access layer
    user_adapter = RabbitMQUserAdapter(logger=user_service_logger)

    # Create use cases
    login_use_case = StubLoginUseCase(  # FOR TESTING PURPOSES ONLY
        user_adapter=user_adapter,
        jwt_service=jwt_service,
        auth_service=auth_service,
        logger=auth_service_logger
    )

    # Create API layer
    rabbitmq_api_gateway_listener = RabbitMQApiGatewayListener(
        login_use_case=login_use_case,
        logger=api_gateway_logger
    )

    return rabbitmq_api_gateway_listener

async def start_api_gateway_rabbitmq_listener(listener: RabbitMQApiGatewayListener):
    """Start the RabbitMQ listener."""
    await listener.start_listening()


async def lifespan(app: FastAPI):
    """FastAPI lifespan event handler for startup and shutdown."""
    # Create dependencies
    listener = await setup_dependencies()

    # Start RabbitMQ listener
    listeners_task = asyncio.create_task(
        start_api_gateway_rabbitmq_listener(listener)
    )

    yield  # Application runs here

    # Cleanup on shutdown
    listeners_task.cancel()
    try:
        await listeners_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8001)
