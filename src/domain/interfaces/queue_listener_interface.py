from abc import ABC, abstractmethod
from typing import Any


class IQueueListener(ABC):
    """
    This is an abstract base class that defines the interface that works with
    queues such as RabbitMQ.
    """
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def start_listening(self) -> None:
        pass

    @abstractmethod
    async def send_response(self, routing_key: str, response: Any, correlation_id: str) -> None:
        pass
