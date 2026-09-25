from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
import jwt
from app.core.config import settings

pwd_context = PasswordHash.recommended()

# para hacer hash ala comtrasena


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# verificar contrasena


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# codificar el token


def create_access_token(data: dict, minutes: int | None = None) -> str:

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes or settings.JWT_EXPIRES_MIN)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

# decodificar el token


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
