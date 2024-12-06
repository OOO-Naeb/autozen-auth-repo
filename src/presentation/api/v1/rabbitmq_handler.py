from src.infrastructure.adapters.rabbitmq_gateway_listener_adapter import RabbitMQGatewayListenerAdapter

async def start_rabbitmq_listener(auth_service):
    queues_listener = RabbitMQGatewayListenerAdapter(auth_service=auth_service)

    await queues_listener.start_listening()
