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


# Тут идет инициализация всех репозиториев при вызове класса
# Тут стоит вопрос оптимизации. По сути, стоимость инита классов маленькая, но если их будет больше
# и вопрос станет ребром, можно сделать через @property
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


# @property repo init variant
class UnitOfWork__TEST:
    def __init__(self):
        self.session = async_session_maker

        self._users = None

    async def __aenter__(self):
        self.session = self.session()

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @property
    def users(self):
        if self._users is None:
            self._users = UserRepository(self.session)
        return self._users
