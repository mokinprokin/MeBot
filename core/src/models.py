
from typing import Optional, Annotated
from datetime import datetime
from typing import Optional, Annotated
from sqlalchemy import MetaData, String, text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
metaDataObj = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[
    datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))
]
updated_at = Annotated[
    datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.utcnow
    ),
]

class UsersOrm(Base):
    __tablename__ = "users"
    
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(150))  
    about: Mapped[str] = mapped_column(String(200))  
    target: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hobby: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    presentation: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)
