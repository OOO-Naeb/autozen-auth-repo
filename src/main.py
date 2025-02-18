from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
import asyncio

from src.application.services.password_hasher import BcryptPasswordHasher
from src.application.services.auth_service import AuthService
from src.application.services.jwt_service import JWTService
from src.application.use_cases.login import LoginUseCase, StubLoginUseCase
from src.application.use_cases.refresh import RefreshUseCase
from src.application.use_cases.register import RegisterUseCase
from src.core.logger import LoggerService
from src.infrastructure.adapters.rabbitmq_api_gateway_listener import RabbitMQApiGatewayListener
from src.infrastructure.adapters.rabbitmq_user_adapter import RabbitMQUserAdapter


async def setup_dependencies():
    """
    Initialize all dependencies.

    This function creates and wires together all the components of our application:
    - Logger
    - Password hasher for secure hashed_password verification
    - Auth service for authentication operations
    - JWT service for token management
    - User adapter for communication with User Service
    - Login use case that orchestrates the authentication flow
    - RabbitMQ listener that handles incoming requests
    """
    logger = LoggerService(__name__, "auth_service_log.log")

    # Create core services
    jwt_service = JWTService()
    bcrypt_password_hasher = BcryptPasswordHasher()
    auth_service = AuthService(password_hasher=bcrypt_password_hasher)

    # Create data access layer
    user_adapter = RabbitMQUserAdapter(logger=logger)

    # Create use cases
    login_use_case = StubLoginUseCase(  # FOR TESTING PURPOSES ONLY!!!
        user_adapter=user_adapter,
        jwt_service=jwt_service,
        auth_service=auth_service,
        logger=logger
    )

    refresh_use_case = RefreshUseCase(
        jwt_service=jwt_service,
        logger=logger
    )

    register_use_case = RegisterUseCase(
        user_adapter=user_adapter,
        password_hasher=bcrypt_password_hasher,
        logger=logger
    )

    # Create API layer
    rabbitmq_api_gateway_listener = RabbitMQApiGatewayListener(
        login_use_case=login_use_case,
        refresh_use_case=refresh_use_case,
        register_use_case=register_use_case,
        logger=logger
    )

    return rabbitmq_api_gateway_listener

async def start_api_gateway_rabbitmq_listener(listener: RabbitMQApiGatewayListener):
    """Start the RabbitMQ listener."""
    await listener.start_listening()


@asynccontextmanager
async def lifespan(_app: FastAPI):
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
