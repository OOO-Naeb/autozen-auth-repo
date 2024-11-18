from src.infrastructure.adapters.rabbitmq_gateway_listener_adapter import RabbitMQGatewayListenerAdapter

async def start_rabbitmq_listener(auth_use_case):
    queues_listener = RabbitMQGatewayListenerAdapter(auth_use_case=auth_use_case)

    await queues_listener.start_listening()
