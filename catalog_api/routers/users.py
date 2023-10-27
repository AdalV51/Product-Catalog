from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from catalog_api.database import database, users_table
from catalog_api.models.users import (
    User,
    UserBase,
    UserCreate,
    UserUpdate,
    UserUpdateIn,
)
from catalog_api.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_user,
    is_user_admin,
)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    is_admin_user: Annotated[bool, Depends(is_user_admin)],
):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that email already exists",
        )

    if user.is_admin and not is_admin_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create admin users",
        )

    hashed_password = get_password_hash(user.password)
    data = user.dict()
    query = users_table.insert().values({**data, "password": hashed_password})
    await database.execute(query)
    return {"detail": "User created successfully"}


@router.post("/token", status_code=status.HTTP_201_CREATED)
async def login_user(user: UserBase):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@router.patch(
    "/user/{user_id}", response_model=UserUpdate, status_code=status.HTTP_200_OK
)
async def partially_update_user(
    user: UserUpdateIn,
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    data = {
        "email": user.email,
        "is_admin": user.is_admin,
    }
    query = users_table.update().where(users_table.c.id == user_id).values(data)
    last_record_id = await database.execute(query)
    if not last_record_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {**data, "id": last_record_id}


@router.delete("/user/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    query = users_table.delete().where(users_table.c.id == user_id)
    deleted_user = await database.execute(query)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"detail": "User deleted sucessfully"}
