import uvicorn
from fastapi import FastAPI
import asyncio

from src.application.use_cases.auth_use_case import AuthUseCase
from src.core.jwt_service import JWTService
from src.infrastructure.adapters.rabbitmq_user_adapter import RabbitMQUserAdapter
from src.presentation.api.v1.rabbitmq_handler import start_rabbitmq_listener

user_adapter = RabbitMQUserAdapter()
jwt_service = JWTService()
auth_use_case = AuthUseCase(user_adapter=user_adapter, jwt_service=jwt_service)

async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_rabbitmq_listener(auth_use_case=auth_use_case))

    yield

    task.cancel()

app = FastAPI(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8001)
