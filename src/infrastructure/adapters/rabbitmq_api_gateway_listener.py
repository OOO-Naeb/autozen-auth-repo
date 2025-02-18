import json
from typing import Callable, Any

import aio_pika

from src.application.exceptions import InvalidCredentialsError, UserNotFoundError, InactiveUserError, \
    InvalidPasswordError, TokenGenerationError
from src.core.config import settings
from src.domain.interfaces.queue_listener_interface import IQueueListener
from src.domain.schemas import RabbitMQResponse
from src.infrastructure.exceptions import RabbitMQError, UserServiceError
from src.core.exceptions import AuthServiceError


class RabbitMQApiGatewayListener(IQueueListener):
    def __init__(
            self,
            login_use_case,
            refresh_use_case,
            register_use_case,
            logger
    ):
        self._login_use_case = login_use_case
        self._refresh_use_case = refresh_use_case
        self._register_use_case = register_use_case
        self._logger = logger

        self._connection = None
        self._channel = None
        self._exchange = None
        self._exchange_name = 'API-GATEWAY-to-AUTH-SERVICE-exchange.direct'

        self._operation_handlers = {
            'login': self._login_use_case.execute,
            'refresh': self._refresh_use_case.execute,
            'register': self._register_use_case.execute,
        }

    async def connect(self) -> None:
        """
        Establishes a connection to the RabbitMQ service.

        Raises:
            RabbitMQError: When RabbitMQ service is not available.
        """
        if not self._connection or self._connection.is_closed:
            try:
                self._connection = await aio_pika.connect_robust(
                    settings.rabbitmq_url,
                    timeout=10,
                    client_properties={'client_name': 'Auth Service'}
                )
                self._channel = await self._connection.channel()
                self._exchange = await self._channel.declare_exchange(
                    self._exchange_name,
                    aio_pika.ExchangeType.DIRECT,
                    durable=True
                )
            except aio_pika.exceptions.AMQPConnectionError as e:
                self._logger.critical(f"RabbitMQ service is unavailable. Connection error: {e}. From: RabbitMQListener, connect().")
                raise RabbitMQError(detail="RabbitMQ service is unavailable.")

        if not self._channel or self._channel.is_closed:
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

    async def _initialize_queue(self) -> None:
        auth_queue = await self._channel.declare_queue(
            'AUTH.all',
            durable=True
        )
        await auth_queue.bind(self._exchange, routing_key='AUTH.all')
        await auth_queue.consume(self._message_handler())

    async def start_listening(self) -> None:
        await self.connect()
        await self._initialize_queue()
        self._logger.info("Started listening for messages in the 'AUTH.all' queue.")

    async def send_response(
            self,
            routing_key: str,
            response: Any,
            correlation_id: str
    ) -> None:
        print(response)
        message = aio_pika.Message(
            body=json.dumps({
                "status_code": response.status_code,
                "body": response.body,
                "success": response.success,
                "error_message": response.error_message,
                "error_origin": response.error_origin
            }).encode(),
            correlation_id=correlation_id
        )
        await self._channel.default_exchange.publish(
            message,
            routing_key=routing_key
        )

    def _message_handler(self) -> Callable:
        async def handler(message: aio_pika.IncomingMessage) -> None:
            async with message.process():
                self._logger.info(f"Received message: {message.body}")
                try:
                    data = json.loads(message.body.decode())
                    operation_type = data.pop("operation_type")
                    operation_handler = self._operation_handlers.get(operation_type)
                    if not operation_handler:
                        self._logger.error(
                            f"Unknown 'operation_type' received in RabbitMQApiGatewayListener, _message_handler(): {operation_type}"
                        )
                        raise AuthServiceError(
                            status_code=404,
                            detail=f"Unknown 'operation_type' received: {operation_type}"
                        )

                    result = await operation_handler(data)

                    status_code = 200
                    if operation_type == 'register':
                        status_code = 201

                    response = RabbitMQResponse.success_response(
                        status_code=status_code,
                        body=result.to_dict(),
                    )

                except (
                        InvalidCredentialsError,
                        UserNotFoundError,
                        InactiveUserError,
                        InvalidPasswordError,
                        TokenGenerationError,
                        AuthServiceError
                ) as e:
                    response = RabbitMQResponse.error_response(
                        status_code=e.status_code,
                        message=str(e),
                        error_origin='Auth Service'
                    )
                except RabbitMQError as e:
                    response = RabbitMQResponse.error_response(
                        status_code=e.status_code,
                        message=str(e),
                        error_origin='RabbitMQ'
                    )
                except UserServiceError as e:
                    response = RabbitMQResponse.error_response(
                        status_code=e.status_code,
                        message=str(e),
                        error_origin='User Service'
                    )
                except Exception as e:
                    self._logger.critical(f"Unhandled error occurred while processing message in RabbitMQApiGatewayListener, _message_handler(): {str(e)}")
                    response = RabbitMQResponse.error_response(
                        status_code=500,
                        message=f"Unhandled error occurred while processing message in the Auth Service: {str(e)}",
                        error_origin='Auth Service'
                    )
                    raise e
                finally:
                    await self.send_response(
                        routing_key=message.reply_to,
                        response=response,
                        correlation_id=message.correlation_id
                    )

        return handler
