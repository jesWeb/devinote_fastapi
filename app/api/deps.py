from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.db import get_session
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


# url donde obtengo el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Note
# get_db() con next(get_session()) estaba mal: next() cierra el generador de inmediato
# por refcount, la sesion se liberaba al pool antes de usarla. FastAPI ya gestiona el
# ciclo de vida si le pasamos el generador directamente.


"""NOta 
esta nueva forma remplaza a la anterior que haviamos viusto 
ejemplo 

db:Session = depends(get_db)

ahora lo nombrareros asi 
db:DBSession

"""
# [tipos de datos, metadadtos a mandar]
DBSession = Annotated[Session, Depends(get_session)]


# *traer el usuario

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession) -> User:

    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except (jwt.InvalidTokenError, ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalido: {e}",
            headers={"WWW-Authenticate": "Bearer"}
        )

    repo = UserRepository(db)
    user = repo.get_by_id(user_id)

    if not user:
        raise credentials_exc

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
