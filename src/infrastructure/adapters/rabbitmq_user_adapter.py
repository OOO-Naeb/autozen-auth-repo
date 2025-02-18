import asyncio
import json
import uuid
from typing import Dict, Any

import aio_pika
from aio_pika import Message, DeliveryMode

from src.core.config import settings
from src.domain.models.user_requests import AddUserRequestDTO
from src.domain.models.user_responses import UserResponseDTO, UserAuthResponseDTO
from src.infrastructure.exceptions import RabbitMQError, UserServiceError
from src.core.exceptions import AuthServiceError
from src.domain.schemas import RabbitMQResponse
from src.domain.interfaces.user_adapter_interface import IUserAdapter


class RabbitMQUserAdapter(IUserAdapter):
    def __init__(self, logger):
        self._logger = logger

        self._connection = None
        self._channel = None
        self._exchange = None
        self._exchange_name = 'AUTH-SERVICE-and-USER-SERVICE-exchange.direct'
        self._queue_name: str = 'USER.all'

    async def connect(self):
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
                self._logger.critical(f"RabbitMQ service is unavailable. Connection error: {e}. From: RabbitMQUserAdapter, connect().")
                raise RabbitMQError(detail="RabbitMQ service is unavailable.")

        if not self._channel or self._channel.is_closed:
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

    async def _make_rpc_call(
            self,
            operation_type: str,
            payload: Dict[str, Any],
            timeout: int = 5
    ) -> RabbitMQResponse | None:
        await self.connect()

        message_body = {
            "operation_type": operation_type,
            **payload
        }

        callback_queue = await self._channel.declare_queue(
            name=f'from-USER-SERVICE-TO-AUTH-SERVICE.response-{uuid.uuid4()}',
            exclusive=True,
            auto_delete=True
        )

        future = asyncio.get_event_loop().create_future()
        correlation_id = str(uuid.uuid4())

        async def on_response(received_message: aio_pika.IncomingMessage):
            if received_message.correlation_id == correlation_id:
                future.set_result(received_message)
                await received_message.ack()

        consumer_tag = await callback_queue.consume(on_response)

        try:
            # Send message
            await self._exchange.publish(
                Message(
                    body=json.dumps(message_body).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT,
                    correlation_id=correlation_id,
                    reply_to=callback_queue.name,
                ),
                routing_key=self._queue_name
            )

            # Wait for response
            message = await asyncio.wait_for(future, timeout)
            user_service_response = json.loads(message.body.decode())

            response = RabbitMQResponse.success_response(
                status_code=user_service_response.get("status_code", 200),
                body=user_service_response.get("body", {})
            )

            return response

        except asyncio.TimeoutError as e:
            self._logger.critical(f"User Service is not responding. From: RabbitMQUserAdapter, _make_rpc_call(): {str(e)}")
            raise UserServiceError(
                status_code=504,
                detail='asyncio.TimeoutError: User Service is not responding.'
            )
        except aio_pika.exceptions.AMQPException as e:
            error_message = "RabbitMQ communication error."
            self._logger.critical(f"{error_message} From: RabbitMQUserAdapter, _make_rpc_call(): {str(e)}")
            raise RabbitMQError(
                status_code=503,
                detail=error_message
            )
        except Exception as e:
            error_message = "Unhandled error occurred while processing a message."
            self._logger.critical(f"{error_message} From: RabbitMQUserAdapter, _make_rpc_call(): {str(e)}")
            raise AuthServiceError(
                status_code=500,
                detail=error_message
            )
        finally:
            # Cancel the consumer tag
            await callback_queue.cancel(consumer_tag)

    async def get_by_id(self, given_id: int, include_password_hash: bool) -> UserResponseDTO | UserAuthResponseDTO:
        response = await self._make_rpc_call(
            'getById',
            {"user_id": given_id}
        )

        if not response.success:
            self._handle_error_response(response)

        if include_password_hash:
            return UserAuthResponseDTO(**response.body)

        return UserResponseDTO.do_not_include_password(**response.body)  # Called this method to exclude hashed_password hash.


    async def get_by_phone_number(self, phone_number: str, include_password_hash: bool) -> UserResponseDTO | UserAuthResponseDTO:
        response = await self._make_rpc_call(
            'getByPhoneNumber',
            {"user_phone_number": phone_number}
        )

        if not response.success:
            self._handle_error_response(response)

        if include_password_hash:
            return UserAuthResponseDTO(**response.body)

        return UserResponseDTO.do_not_include_password(**response.body)  # Called this method to exclude hashed_password hash.

    async def get_by_email(self, email: str, include_password_hash: bool) -> UserResponseDTO | UserAuthResponseDTO:
        response = await self._make_rpc_call(
            'getByEmail',
            {"user_email": email}
        )

        if not response.success:
            self._handle_error_response(response)

        if include_password_hash:
            return UserAuthResponseDTO(**response.body)

        return UserResponseDTO.do_not_include_password(**response.body)  # Called this method to exclude hashed_password hash.


    async def add(self, user_data: AddUserRequestDTO) -> UserResponseDTO:
        response = await self._make_rpc_call(
            'addUser',
            user_data.to_dict()
        )

        if not response.success:
            self._handle_error_response(response)

        return UserResponseDTO.do_not_include_password(**response.body)  # Called this method to exclude hashed_password hash.

    def _handle_error_response(self, response: RabbitMQResponse):
        if response.status_code == 400:
            raise UserServiceError(
                status_code=400,
                detail=response.error_message
            )
        elif response.status_code == 404:
            raise UserServiceError(
                status_code=404,
                detail=response.error_message
            )
        elif response.status_code == 504:
            raise UserServiceError(
                status_code=504,
                detail='asyncio.TimeoutError: User Service is not responding.'
            )
        elif response.status_code == 500 and response.error_origin == 'User Service':
            self._logger.critical(f"User Service error occurred. From: RabbitMQUserAdapter, _handle_error_response(): {response.error_message}")
            raise UserServiceError(
                status_code=500,
                detail=response.error_message
            )
        else:
            raise AuthServiceError(
                status_code=500,
                detail='Unhandled error occurred while processing the response.'
            )
