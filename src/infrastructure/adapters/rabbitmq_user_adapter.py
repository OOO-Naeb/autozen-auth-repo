import asyncio
import json
import uuid
import datetime
from typing import Dict, Any

import aio_pika
from aio_pika import Message, DeliveryMode

from src.core.config import settings
from src.infrastructure.exceptions import RabbitMQError, UserServiceError, AuthServiceError
from src.domain.models.user import User
from src.domain.schemas import RabbitMQResponse
from src.domain.interfaces.user_adapter_interface import IUserAdapter


class RabbitMQUserAdapter(IUserAdapter):
    def __init__(
            self,
            logger
    ):
        self._logger = logger

        self._connection = None
        self._channel = None
        self._exchange = None
        self._exchange_name = 'AUTH-USER-EXCHANGE.direct'
        self._queue_name: str = 'USER.all'

    def _to_domain(self, user_data: Dict[str, Any]) -> User:
        """
        Converts the data received from RabbitMQ to a User domain model.
        """
        return User(
            id=uuid.UUID(user_data['id']),
            email=user_data.get('email'),
            phone_number=user_data.get('phone_number'),
            hashed_password=user_data['password'],
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            is_active=user_data['is_active'],
            roles=user_data['roles'],
            created_at=datetime.date.fromisoformat(user_data['created_at']),
            updated_at=datetime.date.fromisoformat(user_data['updated_at'])
        )

    async def connect(self):
        """
        Establishes a connection to the RabbitMQ service.

        Raises:
            SourceUnavailableException: When RabbitMQ service is not available.
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
                self._logger.critical(f"RabbitMQ service is unavailable. Connection error: {e}. From: RabbitMQUserAdapter, connect().")
                raise RabbitMQError(detail="RabbitMQ service is unavailable.")


    async def _make_rpc_call(
            self,
            operation_type: str,
            payload: Dict[str, Any],
            timeout: int = 5
    ) -> RabbitMQResponse | None:
        """
        Sends an RPC call through RabbitMQ to the User Service and waits for the response.

        Args:
            operation_type: Operation type to be called as handler-method in User Service
            payload: Request body to send
            timeout: Timeout for waiting for the response

        Returns:
            RabbitMQResponse containing the service response

        Raises:
            SourceUnavailableException: When RabbitMQ or User Service is unavailable
            UserServiceError: When User Service returns an error
            UnhandledException: For unexpected errors
        """
        await self.connect()

        message_body = {
            "operation_type": operation_type,
            **payload
        }

        callback_queue = await self._channel.declare_queue(
            name=f'AUTH-USER.response-{uuid.uuid4()}',
            exclusive=True,
            auto_delete=True
        )

        future = asyncio.get_event_loop().create_future()
        correlation_id = str(uuid.uuid4())

        async def on_response(received_message: aio_pika.IncomingMessage):
            if received_message.correlation_id == correlation_id:
                future.set_result(received_message)

        consumer_tag = await callback_queue.consume(on_response)

        response: RabbitMQResponse

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
            # Clean up
            await callback_queue.cancel(consumer_tag)
            if self._channel and not self._channel.is_closed:
                await self._channel.close()

    async def get_by_id(self, given_id: int) -> User:
        """
        Retrieves a user by their ID from the User Service.

        Args:
            given_id: The ID of the user to retrieve

        Returns:
            User: Domain model of the retrieved user

        Raises:
            UserServiceError: When User Service returns an error
            RabbitMQError: When RabbitMQ connection fails
            AuthServiceError: For unhandled errors
        """
        response = await self._make_rpc_call(
            'getById',
            {"user_id": given_id}
        )

        if not response.success:
            self._handle_error_response(response)

        return self._to_domain(response.body)

    async def get_by_phone_number(self, phone_number: str) -> User:
        """
        Retrieves a user by their phone number from the User Service.

        Args:
            phone_number: The phone number of the user to retrieve

        Returns:
            User: Domain model of the retrieved user

        Raises:
            UserServiceError: When User Service returns an error
            RabbitMQError: When RabbitMQ connection fails
            AuthServiceError: For unhandled errors
        """
        response = await self._make_rpc_call(
            'getByPhoneNumber',
            {"user_phone_number": phone_number}
        )

        if not response.success:
            self._handle_error_response(response)

        return self._to_domain(response.body)

    async def get_by_email(self, email: str) -> User:
        """
        Retrieves a user by their email from the User Service.

        Args:
            email: The email of the user to retrieve

        Returns:
            User: Domain model of the retrieved user

        Raises:
            UserServiceError: When User Service returns an error
            RabbitMQError: When RabbitMQ connection fails
            AuthServiceError: For unhandled errors
        """
        response = await self._make_rpc_call(
            'getByEmail',
            {"user_email": email}
        )

        if not response.success:
            self._handle_error_response(response)

        return self._to_domain(response.body)

    async def add(self, user: User) -> User:
        """
        Adds a new user to the DB through User Service.

        Args:
            user: User domain model data

        Returns:
            User: Domain model of the retrieved user

        Raises:
            UserServiceError: When User Service returns an error
            RabbitMQError: When RabbitMQ connection fails
            AuthServiceError: For unhandled errors
        """
        response = await self._make_rpc_call(
            'addUser',
            user.to_serializable_dict() # Converts datetime objects to strings. Otherwise, JSON serialization will fail.
        )

        if not response.success:
            self._handle_error_response(response)

        return self._to_domain(response.body)

    def _handle_error_response(self, response: RabbitMQResponse):
        """
        Handles the error responses.
        """
        if response.status_code == 400:
            raise UserServiceError(
                status_code=400,
                detail=response.error_message
            )
        elif response.status_code == 503:
            raise RabbitMQError(
                status_code=503,
                detail='RabbitMQ connection error occurred.'
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
                detail='Unhandled error occurred while sending a message.'
            )
