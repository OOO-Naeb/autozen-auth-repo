import uvicorn
from fastapi import FastAPI
import asyncio

from src.presentation.api.v1.rabbitmq_handler import start_rabbitmq_listener



async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_rabbitmq_listener())

    yield

    task.cancel()

app = FastAPI(lifespan=lifespan)


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8001)

