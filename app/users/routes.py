from typing import List

from fastapi import Query
from fastapi.routing import APIRouter

from app.api.dependecies import UOWDep
from app.users.schema import UserSchema, UserSchemaAdd, UserSchemaEdit
from app.users.service import UserService

route = APIRouter(prefix="/user", tags=["Users"])


@route.post("/")
async def add_user(
    user: UserSchemaAdd,
    uow: UOWDep,
):
    user = await UserService().add_user(uow, user)
    return user


@route.post("/{user_id}")
async def edit_user(
    user_id: int,
    user: UserSchemaEdit,
    uow: UOWDep,
):
    user = await UserService().edit_user(user_id, uow, user)
    return user


@route.delete("/{user_id}")
async def delete_user(
    user_id: int,
    uow: UOWDep,
):
    user = await UserService().delete_user(user_id, uow)
    return user


@route.get("/all", response_model=List[UserSchema])
async def find_users(
    uow: UOWDep,
    limit: int = Query(gt=0, le=100, default=10),
    offset: int = Query(ge=0, default=0),
):
    users = await UserService().find_all(uow, limit, offset)
    return users


@route.post("/check")
async def check_user(
    user: UserSchemaAdd,
    uow: UOWDep,
):
    res = await UserService().check_user(uow, user)
    return res


@route.post("/longest_usernames")
async def users_with_longest_username(
    uow: UOWDep,
    limit: int = Query(gt=0, le=100, default=10),
):
    users = await UserService().find_users_with_longest_username(uow, limit)
    return users


@route.get("/by_last_days")
async def user_by_last_days(
    uow: UOWDep,
    days: int = Query(gt=0, le=100, default=1),
):
    """Находит пользователей которые были зарегстрированы за последние дни

    :param days: Дни
    :type days: int
    """
    users = await UserService().find_latest_users_by_days(uow, days)
    return users
