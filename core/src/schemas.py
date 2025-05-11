from typing import Optional
from pydantic import BaseModel


class UserPostDTO(BaseModel):
    name: str
    about:str
    target:Optional[str]
    hobby:Optional[str]
    presentation:Optional[str]


class UserDTO(UserPostDTO):
    id: int



