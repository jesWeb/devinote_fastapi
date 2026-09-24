from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


# url donde obtengo el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

#* acceder a db 
def get_db() -> Session:
    return next(get_session())


"""NOta 
esta nueva forma remplaza a la anterior que haviamos viusto 
ejemplo 

db:Session = depends(get_db)

ahora lo nombrareros asi 
db:DBSession

"""
# [tipos de datos, metadadtos a mandar]
DBSession = Annotated[Session, Depends(get_db)]


# *traer el usuario

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession) -> User:

    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="NO AUTORIZADO",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))

    except Exception:
        raise credentials_exc

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if not user:
        raise credentials_exc

    return user

CurrentUser =Annotated[User,Depends(get_current_user)]