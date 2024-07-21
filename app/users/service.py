import pandas as pd
from fastapi.exceptions import HTTPException
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from starlette import status

from app.database.session import sync_engine
from app.services.unitofwork import IUnitOfWork
from app.users.schema import UserSchema, UserSchemaAdd, UserSchemaEdit


class UserService:
    async def add_user(
        self,
        uow: IUnitOfWork,
        user_schema: UserSchemaAdd,
    ) -> UserSchema:
        user_dict = user_schema.model_dump()
        async with uow:
            exists = await uow.users.check_user(user_schema.username, user_schema.email)
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Юзер с таким username или email уже существует",
                )

            user = await uow.users.add_one(user_dict)
            await uow.commit()
            return user

    async def edit_user(
        self,
        id: int,
        uow: IUnitOfWork,
        user_schema: UserSchemaEdit,
    ) -> UserSchema:
        async with uow:
            exists = await uow.users.find_one(id=id)
            if not exists:
                raise HTTPException(status_code=404, detail="Юзера не существует")

            user_dict = user_schema.model_dump(exclude_none=True)
            user = await uow.users.edit_one(id, user_dict)
            await uow.commit()
            return user

    async def delete_user(
        self,
        id: int,
        uow: IUnitOfWork,
    ) -> UserSchema:
        async with uow:
            exists = await uow.users.find_one(id=id)
            if not exists:
                raise HTTPException(status_code=404, detail="Юзера не существует")

            user = await uow.users.delete_one(id)
            await uow.commit()
            return user

    async def find_user(
        self,
        user_id: int,
        uow: IUnitOfWork,
    ) -> UserSchema:
        async with uow:
            user = await uow.users.find_one(id=user_id)
            if user is None:
                raise HTTPException(status_code=404, detail="Юзера не существует")
            return user

    async def check_user(
        self,
        uow: IUnitOfWork,
        user: UserSchemaAdd,
    ) -> UserSchema:
        async with uow:
            return await uow.users.check_user(user.username, user.email)

    async def find_all(
        self,
        uow: IUnitOfWork,
        limit: int,
        offset: int,
    ) -> list[UserSchema]:
        async with uow:
            return await uow.users.find_all(limit, offset)

    async def find_users_with_longest_username(
        self,
        uow: IUnitOfWork,
        limit: int,
    ) -> list[UserSchema]:
        async with uow:
            return await uow.users.find_users_with_longest_username(limit)

    async def find_latest_users_by_days(
        self,
        uow: IUnitOfWork,
        days: int,
    ) -> list[UserSchema]:
        async with uow:
            return await uow.users.find_latest_users_by_days(days)

    async def count_users_by_email_domain(
        self,
        uow: IUnitOfWork,
        email_domain: str,
    ):
        # Получаем домен, если была отправлена почтв
        domain: str = email_domain.split("@")[-1]
        async with uow:
            return await uow.users.count_users_with_specific_email_domain(domain)


class VisitAnalyticService:
    """
    Класс для анализа на основе машинного обучения,
    который предсказывает активность пользователя в следующем месяце

    P.S. По хорошему нужно ml вынести в отдельный микросервис или отдельное приложение
    Для простоты будет тут

    P.S.S. Без понятия как тренировать модель, никогда не работал с sklearn
    То что ниже, это взято с CHATGPT. Но я все же решил, что не буду эту часть писать.
    Даже если будет работать, я не буду знать как.
    """

    async def execute(self):
        visits_df = pd.read_sql_table("visits", sync_engine)
        # Добавляем признак "активный в следующем месяце"
        visits_df["active_next_month"] = visits_df.groupby("user_id")[
            "visit_date"
        ].apply(lambda x: (x.max() + pd.Timedelta(days=30)) > pd.Timestamp("now"))

        # Преобразуем данные в формат, подходящий для модели машинного обучения
        X = (
            visits_df[["visit_date", "duration", "pages_visited", "traffic_source"]]
            .groupby("user_id")
            .agg(["count", "mean", "max", "min"])
            .reset_index()
        )
        X.columns = ["_".join(col) for col in X.columns.ravel()]
        y = (
            visits_df["active_next_month"]
            .groupby("user_id")
            .max()
            .reset_index()["active_next_month"]
        )

        # Разбиваем данные на обучающую и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Обучаем модель
        model = LogisticRegression()
        model.fit(X_train, y_train)

        # Проверяем модель на тестовой выборке
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        confusion_matrix(y_test, y_pred)
