from loguru import logger
from sqlalchemy import func, or_, select

from app.users.models import User
from app.utils.repository import AbstractRepository


class UserRepository(AbstractRepository):
    model = User

    async def check_user(
        self,
        username: str = "",
        email: str = "",
    ):
        """Проверяем есть ли email или пароль в базе перед добавлением

        :param username: username пользователя, defaults to ""
        :type username: str, optional
        :param email: username пользователя, defaults to ""
        :type email: str, optional
        :return: UserSchema
        """
        stmt = select(self.model).filter(
            or_(
                self.model.email == email,
                self.model.username == username,
            )
        )
        res = await self.session.execute(stmt)
        user = res.scalar_one_or_none()
        if user is not None:
            return user.to_read_model()
        else:
            return None

    async def find_users_with_longest_username(self, limit: int):
        """Находит пользователей с самыми длинными username

        :param limit: Лимит
        :type limit: int
        :return: UserSchema
        :rtype: _type_
        """
        stmt = select(self.model)
        stmt = stmt.order_by(func.length(self.model.username).desc()).limit(limit)

        res = await self.session.execute(stmt)
        res = [row[0].to_read_model() for row in res.all()]

        return res

    async def find_latest_users_by_days(self, days: int):
        """Находит пользователей которые были зарегстрированы за последние дни

        :param days: Дни
        :type days: int
        :return: UserSchema
        :rtype: _type_
        """
        stmt = select(self.model).filter(
            self.model.registration_date >= func.datetime("now", f"-{days} days")
        )
        logger.debug(stmt)

        res = await self.session.execute(stmt)
        res = [row[0].to_read_model() for row in res.all()]

        return res
