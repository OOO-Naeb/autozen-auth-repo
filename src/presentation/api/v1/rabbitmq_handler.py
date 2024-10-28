from src.infrastructure.adapters.rabbitmq_listener_adapter import RabbitMQListenerAdapter

async def start_rabbitmq_listener(auth_use_case):
    queues_listener = RabbitMQListenerAdapter(queue_name='AUTH', auth_use_case=auth_use_case)

    await queues_listener.start_listening()
