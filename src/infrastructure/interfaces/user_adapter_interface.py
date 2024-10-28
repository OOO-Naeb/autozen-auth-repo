from abc import ABC, abstractmethod

from src.domain.schemas import UserFromDB, UserToDB


class IUserAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass

    async def rpc_call(self, routing_key: str, body: dict, timeout: int):
        pass

    async def get_by_id(self, given_id: int) -> UserFromDB:
        pass

    async def get_by_phone_number(self, phone_number: str) -> UserFromDB:
        pass

    async def get_by_email(self, email: str) -> UserFromDB:
        pass

    async def add(self, data: UserToDB) -> UserFromDB:
        pass