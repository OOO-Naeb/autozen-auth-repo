from abc import ABC, abstractmethod


class IQueueListener(ABC):
    """
    This is an abstract base class that defines the interface that works with
    queues such as RabbitMQ.
    """

    @abstractmethod
    def start_listening(self):
        pass
