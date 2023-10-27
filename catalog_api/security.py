import datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from catalog_api.config import config
from catalog_api.database import database, users_table
from catalog_api.models.users import User

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

not_admin_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Only admin can access this",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(email: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    query = users_table.select().where(users_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        raise credentials_exception
    if not verify_password(password, user.password):
        raise credentials_exception
    return user


async def create_default_admin():
    query = users_table.select().where(users_table.c.email == config.DB_ADMIN_EMAIL)
    default_admin_user = await database.fetch_one(query)
    if not default_admin_user:
        hashed_password = get_password_hash(config.DB_ADMIN_PWD)
        query = users_table.insert().values(
            {
                "email": config.DB_ADMIN_EMAIL,
                "password": hashed_password,
                "is_admin": True,
            }
        )
        await database.execute(query)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except Exception:
        raise credentials_exception
    user = await get_user(email=email)
    if user is None:
        raise credentials_exception
    if not user.is_admin:
        raise not_admin_exception
    return user


async def is_user_valid(token: Annotated[str, Depends(oauth2_scheme)]) -> bool:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return False
    except (ExpiredSignatureError, Exception):
        return False

    user = await get_user(email=email)
    if user is None:
        return False

    return True


async def is_user_admin(token: Annotated[str, Depends(oauth2_scheme)]) -> bool:
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return False
    except (ExpiredSignatureError, Exception):
        return False

    user = await get_user(email=email)
    if user is None:
        return False

    if user.is_admin:
        return True
    else:
        return False
