from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import AsyncSessionLocal, Base, async_engine
from ..models import UsersOrm

class AsyncOrm:
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_user(
        id: int,
        name: str,
        about: str,
        target: str | None = None,
        hobby: str | None = None,
    ) -> UsersOrm:
        async with AsyncSessionLocal() as session:
            user = UsersOrm(
                id=id,
                name=name,
                about=about,
                target=target,
                hobby=hobby,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def update_user_presentation(user_id: int, presentation_text: str) -> None:
        async with AsyncSessionLocal() as session:
            await session.execute(
                update(UsersOrm)
                .where(UsersOrm.id == user_id)
                .values(presentation=presentation_text)
            )
            await session.commit()

    @staticmethod
    async def update_user_item(user_id: int, **kwargs) -> None:
        async with AsyncSessionLocal() as session:
            if not kwargs:
                raise ValueError("Не указаны поля для обновления")

            await session.execute(
                update(UsersOrm)
                .where(UsersOrm.id == user_id)
                .values(**kwargs)
            )
            await session.commit()

    @staticmethod
    async def get_user_by_id(user_id: int) -> UsersOrm | None:
        async with AsyncSessionLocal() as session:
            result = await session.get(UsersOrm, user_id)
            return result
