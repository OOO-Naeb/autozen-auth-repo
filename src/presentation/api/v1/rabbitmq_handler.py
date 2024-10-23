from src.infrastructure.adapters.rabbitmq_listener_adapter import RabbitMQListenerAdapter

async def start_rabbitmq_listener():
    queue_listener = RabbitMQListenerAdapter(queue_name='AUTH.register')
    await queue_listener.start_listening()
