

from sqlmodel import SQLModel, Field


# * crear tabla  con sqlmodel
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str = Field(default='')
    hashed_password: str


# * crear clases ose a como pydantic -> esta la convietre automaticamente en la validaciond e pydentic implicitamente es
class UserCreate(SQLModel):
    email: str
    full_name: str = ""
    password: str


class UserRead():
    id: int
    email: str
    full_name: str
    # le dice a pydantic que puede crear el modelo a partir de un objeto con atributos
    model_config = {"from_attributes": True}
