import asyncio
import json
import logging
import os
import uuid

import aio_pika

from src.core.config import settings
from src.domain.exceptions import SourceUnavailableException, SourceTimeoutException, \
    NotFoundException, UnhandledException, AccessDeniedException
from src.domain.schemas import UserFromDB, UserToDB
from src.infrastructure.interfaces.user_adapter_interface import IUserAdapter


class RabbitMQUserAdapter(IUserAdapter):
    def __init__(self):
        self.logger =logging.getLogger(__name__)

        log_dirs = 'logs'
        if not os.path.exists(log_dirs):
            os.makedirs(log_dirs)

        log_format = '%(levelname)s:    %(asctime)s - %(name)s: %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

        file_handler = logging.FileHandler(os.path.join(log_dirs, 'users_log.log'))
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.DEBUG)

        self.connection = None
        self.channel = None
        self.exchange = None
        self.exchange_name = 'AUTH-USERS-EXCHANGE.direct'

    async def connect(self):
        """
        Establishes a connection to the RabbitMQ service.

        Raises:
            SourceUnavailableException: When RabbitMQ service is not available.
        """
        if self.connection or self.connection.is_closed:
            try:
                self.connection = await aio_pika.connect_robust(
                    settings.rabbitmq_url,
                    timeout=10,
                    client_properties={'client_name': 'User Service'}
                )
                self.channel = self.connection.channel()
                self.exchange = await self.channel.declare_exchange(
                    self.exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
                )
            except aio_pika.exceptions.AMQPConnectionError:
                self.logger.error(
                    "RabbitMQ service is unavailable. Connection error. From: RabbitMQAuthAdapter, connect()."
                )
                raise SourceUnavailableException()


    async def rpc_call(self, routing_key: str, body: dict, timeout: int = 5) -> tuple:
        """
        Sends an RPC call through RabbitMQ and waits for the response.

        Args:
            routing_key (str): The routing key for the RabbitMQ queue.
            body (dict): The request body to send.
            timeout (int): Timeout for waiting for the response.

        Returns:
            tuple: status_code (int), response_body (dict)

        Raises:
            SourceTimeoutException: If the response takes too long.
        """
        await self.connect()

        callback_queue = self.channel.declare_queue(
            name=f'FOR-AUTH-RESPONSE-QUEUE-{uuid.uuid4()}',
            exclusive=True,
            auto_delete=True
        )
        correlation_id = str(uuid.uuid4())

        # Dev logs
        print("Generated correlation ID from sender ->", correlation_id)

        rabbit_mq_response_future =asyncio.get_event_loop().create_future()

        async def on_response(response_message: aio_pika.IncomingMessage):
            if response_message.correlation_id == correlation_id:
                rabbit_mq_response_future.set_result(response_message)

        consumer_tag = await callback_queue.consume(on_response)

        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                correlation_id=correlation_id,
                reply_to=callback_queue.name,
            ),
            routing_key=routing_key,
        )

        try:
            message = await asyncio.wait_for(rabbit_mq_response_future, timeout)

            response = json.loads(message.body.decode())
            status_code = response.get("status_code", 500)
            response_body = response.get("body", {})

            return status_code, response_body

        except asyncio.TimeoutError:
            self.logger.error(
                "User Service is unavailable. No response. From: RabbitMQUserAdapter, rpc_call()."
            )
            raise SourceTimeoutException()

        finally:
            await callback_queue.cancel(consumer_tag)
            if not self.channel.is_closed:
                await self.channel.close()


    async def get_by_id(self, given_id: int) -> UserFromDB:
        body = {'user_id': given_id}
        status_code, response_body = await self.rpc_call('USERS.get', body)

        if status_code == 403:
            raise AccessDeniedException()
        elif status_code == 404:
            raise NotFoundException()
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter in get_by_id(): {status_code} | {response_body}")
            raise UnhandledException()

        return UserFromDB(**response_body)

    async def get_by_phone_number(self, phone_number: str) -> UserFromDB:
        body = {'user_phone_number': phone_number}
        status_code, response_body = await self.rpc_call('USERS.get', body)

        if status_code == 403:
            raise AccessDeniedException()
        elif status_code == 404:
            raise NotFoundException()
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter in get_by_phone_number(): {status_code} | {response_body}")
            raise UnhandledException()

        return UserFromDB(**response_body)

    async def get_by_email(self, email: str) -> UserFromDB:
        body = {'user_email': email}
        status_code, response_body = await self.rpc_call('USERS.get', body)

        if status_code == 403:
            raise AccessDeniedException()
        elif status_code == 404:
            raise NotFoundException()
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter in get_by_email(): {status_code} | {response_body}")
            raise UnhandledException()

        return UserFromDB(**response_body)

    async def add(self, data: UserToDB) -> UserFromDB:
        status_code, response_body = await self.rpc_call('USERS.post', data.model_dump())

        if status_code == 403:
            raise AccessDeniedException()
        elif status_code >= 404:
            raise NotFoundException()
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter in add(): {status_code} | {response_body}")
            raise UnhandledException()

        return UserFromDB(**response_body)

