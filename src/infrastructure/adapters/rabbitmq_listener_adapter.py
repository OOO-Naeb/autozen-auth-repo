import asyncio
import json
import logging
from typing import Callable

import aio_pika
import threading

from src.application.use_cases.auth_use_case import AuthUseCase
from src.core.config import settings
from src.domain.exceptions import SourceUnavailableException
from src.domain.schemas import RegisterRequestForm
from src.infrastructure.interfaces.queue_listener_interface import IQueueListener


class RabbitMQListenerAdapter(IQueueListener):
    def __init__(self, auth_use_case: AuthUseCase) -> None:
        self.logger = logging.getLogger(__name__)
        self.auth_use_case = auth_use_case
        self.connection = None
        self.channel = None
        self.exchange_name = 'GATEWAY-AUTH-EXCHANGE.direct'
        self.routes = {
            'AUTH.register': self.call_register,
            'AUTH.login': self.call_login,
            'AUTH.refresh': self.call_refresh
        }

    async def start_listening(self) -> None:
        thread = threading.Thread(target=self._listen, daemon=True)
        thread.start()

    def _listen(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._initialize_queues(loop))
        loop.run_forever()

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = await aio_pika.connect_robust(
                    settings.rabbitmq_url,
                    timeout=10,
                    client_properties={'client_name': 'Auth Service'}
                )
                self.channel = await self.connection.channel()
                await self.channel.declare_exchange(self.exchange_name, aio_pika.ExchangeType.DIRECT, durable=True)

            except aio_pika.exceptions.AMQPConnectionError:
                self.logger.error(
                    f"RabbitMQ service is unavailable. Connection error. From: RabbitMQListenerAdapter, connect()."
                )
                raise SourceUnavailableException(detail="RabbitMQ service is unavailable.")

    async def _initialize_queues(self, loop):
        await self.connect()

        for routing_key, handler in self.routes.items():
            queue_name = routing_key
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.bind(self.exchange_name, routing_key)
            await queue.consume(self._create_callback(handler, loop))

            print(
                f'[*] Waiting for messages in queues: {[f"{self.exchange_name}.{key}" for key in self.routes.keys()]}')

    def _create_callback(self, handler: Callable, loop):
        async def callback(message: aio_pika.IncomingMessage):
            async with message.process():
                print(f"[X] Received message from {message.routing_key} - {message.body}")
                data = json.loads(message.body)

                # Dev logs
                print("Correlation ID from receiver ->", message.correlation_id)
                print("To send back to:", message.reply_to)

                response = await handler(data)

                response_message = json.dumps({
                    "status_code": 200,
                    "body": response.dict()
                })

                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=response_message.encode(),
                        correlation_id=message.correlation_id
                    ),
                    routing_key=message.reply_to
                )

        return lambda msg: asyncio.run_coroutine_threadsafe(callback(msg), loop)

    async def call_register(self, data: dict):
        from src.presentation.api.v1.auth_routes import register
        return await register(data, self.auth_use_case)

    async def call_login(self, data):
        from src.presentation.api.v1.auth_routes import login
        return await login(data, self.auth_use_case)

    async def call_refresh(self, data):
        from src.presentation.api.v1.auth_routes import refresh
        return await refresh(data, self.auth_use_case)
