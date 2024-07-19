from fastapi.exceptions import HTTPException
from loguru import logger
from starlette import status

from app.services.unitofwork import IUnitOfWork
from app.users.schema import UserSchemaAdd, UserSchemaEdit


class UserService:
    async def add_user(
        self,
        uow: IUnitOfWork,
        user: UserSchemaAdd,
    ):
        user_dict = user.model_dump()
        async with uow:
            exists = await uow.users.check_user(user.username, user.email)
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Юзер с таким username или email уже существует",
                )

            user_id = await uow.users.add_one(user_dict)
            await uow.commit()
            return user_id

    async def edit_user(
        self,
        id: int,
        uow: IUnitOfWork,
        user: UserSchemaEdit,
    ):
        async with uow:
            exists = await uow.users.find_one(id=id)
            if not exists:
                raise HTTPException(status_code=404, detail="Юзера не существует")

            user_dict = user.model_dump()
            res = await uow.users.edit_one(id, user_dict)
            await uow.commit()
            return res

    async def delete_user(
        self,
        id: int,
        uow: IUnitOfWork,
    ):
        async with uow:
            exists = await uow.users.find_one(id=id)
            if not exists:
                raise HTTPException(status_code=404, detail="Юзера не существует")

            user_id = await uow.users.delete_one(id)
            await uow.commit()
            return user_id

    async def find_user(
        self,
        uow: IUnitOfWork,
        user: UserSchemaAdd,
    ):
        async with uow:
            user_id = await uow.users.find_one(username="asdasd")
            await uow.commit()
            return user_id

    async def check_user(
        self,
        uow: IUnitOfWork,
        user: UserSchemaAdd,
    ):
        async with uow:
            return await uow.users.check_user(user.username, user.email)

    async def find_all(
        self,
        uow: IUnitOfWork,
        limit: int,
        offset: int,
    ):
        async with uow:
            return await uow.users.find_all(limit, offset)

    async def find_users_with_longest_username(
        self,
        uow: IUnitOfWork,
        limit: int,
    ):
        async with uow:
            return await uow.users.find_users_with_longest_username(limit)

    async def find_latest_users_by_days(
        self,
        uow: IUnitOfWork,
        days: int,
    ):
        async with uow:
            return await uow.users.find_latest_users_by_days(days)
