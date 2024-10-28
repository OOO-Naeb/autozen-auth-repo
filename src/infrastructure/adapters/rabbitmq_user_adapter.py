import json
import logging
import time
import uuid

import pika
from pika import exceptions

from src.domain.exceptions import SourceUnavailableException, SourceTimeoutException, \
    NotFoundException, UnhandledException, AccessDeniedException
from src.domain.schemas import UserFromDB, UserToDB
from src.infrastructure.interfaces.user_adapter_interface import IUserAdapter


class RabbitMQUserAdapter(IUserAdapter):
    def __init__(self):
        self.logger =logging.getLogger(__name__)
        self.connection = None
        self.channel = None
        self.exchange_name = None

    async def connect(self):
        if self.connection is None or self.channel is None:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='direct', durable=True)
            except pika.exceptions.AMQPConnectionError:
                self.logger.error(f"RabbitMQ service is unavailable. Connection error. From: RabbitMQAuthAdapter, connect().")
                raise SourceUnavailableException(detail="RabbitMQ service is unavailable.")

    async def rpc_call(self, routing_key: str, body: dict, timeout: int = 5):
        await self.connect()

        queue_for_responses = self.channel.queue_declare(queue='', exclusive=True)
        callback_queue = queue_for_responses.method.queue

        corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,
            body=json.dumps(body),
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id,
                delivery_mode=2,
            )
        )

        response = None
        status_code = None
        response_body = None
        response_start_time = time.time()

        def on_response(ch, method, props, body):
            nonlocal response, status_code, response_body
            if props.correlation_id == corr_id:
                response = json.loads(body)
                status_code = response.get('status_code', 500)
                response_body = response.get('body', {})

        self.channel.basic_consume(
            queue=callback_queue,
            on_message_callback=on_response,
            auto_ack=True,
        )

        while response is None:
            self.connection.process_data_events()
            if time.time() > response_start_time + timeout:
                self.logger.error(f"Timeout while waiting for response from 'AuthService' microservice. From: RabbitMQAuthAdapter, rpc_call().")
                raise SourceTimeoutException(detail="Timeout waiting for response from 'AuthService' microservice.")

        return status_code, response_body

    async def get_by_id(self, given_id: int) -> UserFromDB:
        body = {'id': given_id}
        status_code, response_body = await self.rpc_call('USER.get_by_id', body)

        if status_code == 403:
            raise AccessDeniedException(detail="Invalid access token.")
        elif status_code == 404:
            raise NotFoundException(detail="Source was not found.")
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter during REFRESHING TOKEN: {status_code} | {response_body}")
            raise UnhandledException()

        return UserFromDB(**response_body)

    async def get_by_phone_number(self, phone_number: str) -> UserFromDB:
        body = {'phone_number': phone_number}
        status_code, response_body = await self.rpc_call('USER.get_by_phone_number', body)

        if status_code == 403:
            raise AccessDeniedException(detail="Invalid access token.")
        elif status_code == 404:
            raise NotFoundException(detail="Source was not found.")
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter during REFRESHING TOKEN: {status_code} | {response_body}")
            raise UnhandledException()

        return UserFromDB(**response_body)

    async def get_by_email(self, email: str) -> UserFromDB:
        body = {'email': email}
        status_code, response_body = await self.rpc_call('USER.get_by_email', body)

        if status_code == 403:
            raise AccessDeniedException(detail="Invalid access token.")
        elif status_code == 404:
            raise NotFoundException(detail="Source was not found.")
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter during REFRESHING TOKEN: {status_code} | {response_body}")
            raise UnhandledException()

        return UserFromDB(**response_body)

    async def add(self, data: UserToDB) -> UserFromDB:
        status_code, response_body = await self.rpc_call('USER.add', data.model_dump())

        if status_code == 403:
            raise AccessDeniedException(detail="Invalid access token.")
        elif status_code >= 404:
            raise NotFoundException(detail="Source was not found.")
        elif status_code >= 400:
            self.logger.error(f"Unknown error in RabbitMQAuthAdapter during REFRESHING TOKEN: {status_code} | {response_body}")
            raise UnhandledException()

        return UserFromDB(**response_body)

