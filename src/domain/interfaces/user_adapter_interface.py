from abc import ABC, abstractmethod

from src.domain.models.user import User


class IUserAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass

    async def rpc_call(self, routing_key: str, body: dict, timeout: int):
        pass

    async def get_by_id(self, given_id: int) -> User:
        pass

    async def get_by_phone_number(self, phone_number: str) -> User:
        pass

    async def get_by_email(self, email: str) -> User:
        pass

    async def add(self, user: User) -> User:
        pass