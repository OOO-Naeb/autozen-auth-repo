import json
import logging
import os
from typing import Callable, Annotated

import aio_pika
from fastapi import Depends

from src.application.services.auth_service import AuthService
from src.core.config import settings
from src.domain.exceptions import SourceUnavailableException
from src.infrastructure.interfaces.queue_listener_interface import IQueueListener


class RabbitMQAPIGatewayListener(IQueueListener):
    def __init__(self, auth_service: Annotated[AuthService, Depends(AuthService)]) -> None:
        # Logging setup --------------------------------------------------------------------------------------------- #
        self.logger = logging.getLogger(__name__)

        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_format = '%(levelname)s:    %(asctime)s - %(name)s: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

        file_handler = logging.FileHandler(os.path.join(log_dir, "api_gateway_log.log"))
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)
        # ----------------------------------------------------------------------------------------------------------- #

        self.auth_service = auth_service
        self.connection = None
        self.channel = None
        self.exchange = None
        self.exchange_name = 'GATEWAY-AUTH-EXCHANGE.direct'
        self.routes = {
            'AUTH.register': self.call_register,
            'AUTH.login': self.call_login,
            'AUTH.refresh': self.call_refresh
        }

    async def start_listening(self) -> None:
        await self.connect()
        await self._initialize_queues()

    async def connect(self):
        """
        ADAPTER METHOD: Establish a connection to the RabbitMQ service.

        Raises:
            SourceUnavailableException: When RabbitMQ service is not available.
        """
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = await aio_pika.connect_robust(
                    settings.rabbitmq_url,
                    timeout=10,
                    client_properties={'client_name': 'Auth Service'}
                )
                self.channel = await self.connection.channel()
                self.exchange = await self.channel.declare_exchange(
                    self.exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
                )
            except aio_pika.exceptions.AMQPConnectionError as e:
                self.logger.error(
                    f"RabbitMQ service is unavailable. Connection error: {e}. From: RabbitMQGatewayListenerAdapter, connect()"
                )
                raise SourceUnavailableException(detail="RabbitMQ service is unavailable.")

    async def _initialize_queues(self):
        await self.connect()

        for routing_key, handler in self.routes.items():
            queue_name = routing_key
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.bind(self.exchange_name, routing_key)
            await queue.consume(self._create_callback(handler))
            print(
                f"[*] Queue '{queue_name}' is bound to exchange '{self.exchange_name}' with routing key '{routing_key}'.")

        print(f"[*] Waiting for messages in queues: {list(self.routes.keys())}")

    def _create_callback(self, handler: Callable):
        async def callback(message: aio_pika.IncomingMessage):
            async with message.process():
                print(f"[X] Received message from {message.routing_key} - {message.body}")
                data = json.loads(message.body)

                # Dev logs
                print("Correlation ID from sender ->", message.correlation_id)
                print("To send back to:", message.reply_to)

                status_code, response = await handler(data)

                response_message = json.dumps({
                    "status_code": status_code,
                    "body": response.dict()
                })

                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=response_message.encode(),
                        correlation_id=message.correlation_id
                    ),
                    routing_key=message.reply_to
                )

        return callback

    async def call_register(self, data: dict):
        return await self.auth_service.register(data)

    async def call_login(self, data):
        return await self.auth_service.login(data)

    async def call_refresh(self, data):
        return await self.auth_service.refresh(data)
