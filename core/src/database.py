from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from .config import settings

# Асинхронный движек (SQLite)
async_engine = create_async_engine(
    url=settings.DATABASE_URL_sqlite.replace("sqlite:///", "sqlite+aiosqlite:///"),
    echo=True,
)

# Асинхронная сессия
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

class Base(DeclarativeBase):
    repr_cols_num = 26
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"