from abc import ABC, abstractmethod
from typing import Type

from app.database.session import async_session_maker
from app.users.repository import UserRepository


class IUnitOfWork(ABC):
    users: Type[UserRepository]

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork:
    def __init__(self):
        self.session = async_session_maker

    async def __aenter__(self):
        self.session = self.session()

        # Инитим репозитории
        self.users = UserRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
