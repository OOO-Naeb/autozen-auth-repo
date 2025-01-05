import uvicorn
from fastapi import FastAPI
import asyncio

from starlette.middleware.base import BaseHTTPMiddleware

from src.application.services.auth_service import AuthService
from src.application.services.jwt_service import JWTService
from src.core.middleware.exceptions_middleware import AuthExceptionMiddleware
from src.infrastructure.adapters.rabbitmq_user_adapter import RabbitMQUserAdapter
from src.presentation.api.v1.rabbitmq_handler import start_rabbitmq_listener

user_adapter = RabbitMQUserAdapter()

jwt_service = JWTService()
auth_service = AuthService(user_adapter=user_adapter, jwt_service=jwt_service)

async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_rabbitmq_listener(auth_service=auth_service))

    yield

    task.cancel()

app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=AuthExceptionMiddleware(app=app).dispatch)


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8001)
