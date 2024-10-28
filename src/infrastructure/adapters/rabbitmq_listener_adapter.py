import asyncio
import json

import pika
import threading

from src.application.use_cases.auth_use_case import AuthUseCase
from src.infrastructure.interfaces.queue_listener_interface import IQueueListener


class RabbitMQListenerAdapter(IQueueListener):
    def __init__(self, queue_name: str, auth_use_case: AuthUseCase) -> None:
        self.queue_name = queue_name
        self.auth_use_case = auth_use_case
        self.routes = {
            'AUTH.register': self.call_register,
            'AUTH.login': self.call_login,
            'AUTH.refresh': self.call_refresh
        }

    async def start_listening(self) -> None:
        thread = threading.Thread(target=self._listen, daemon=True)
        thread.start()

    def _listen(self) -> None:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        exchange_name = 'AUTH.direct'
        channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)

        channel.queue_declare(queue=self.queue_name)
        for routing_key in self.routes.keys():
            channel.queue_bind(exchange=exchange_name, queue=self.queue_name, routing_key=routing_key)

        channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=False)

        print(f'[*] Waiting for messages in queue: {self.queue_name}.')
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        routing_key = method.routing_key
        print(f'[X] Received from {self.queue_name} with routing key {routing_key} - {body}')

        data = json.loads(body)

        if routing_key in self.routes:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            response = loop.run_until_complete(self.routes[routing_key](data))

            response_data = response.dict()

            response_message = json.dumps({
                "status_code": 200,
                "body": response_data
            })

            ch.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(
                    correlation_id=properties.correlation_id
                ),
                body=response_message
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print(f"Unknown routing key: {routing_key}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    async def call_register(self, data):
        from src.presentation.api.v1.auth_routes import register
        return await register(data, self.auth_use_case)

    async def call_login(self, data):
        from src.presentation.api.v1.auth_routes import login
        return await login(data, self.auth_use_case)

    async def call_refresh(self, data):
        from src.presentation.api.v1.auth_routes import refresh
        return await refresh(data, self.auth_use_case)
