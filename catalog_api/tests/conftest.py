import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

os.environ["ENV_STATE"] = "test"
from catalog_api.config import config  # noqa: E402
from catalog_api.database import database, users_table  # noqa: E402
from catalog_api.main import app  # noqa: E402
from catalog_api.security import create_default_admin, is_user_admin  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url=client.base_url) as ac:
        yield ac


@pytest.fixture()
async def admin_credentials() -> str:
    await create_default_admin()
    return {"email": config.DB_ADMIN_EMAIL, "password": config.DB_ADMIN_PWD}


@pytest.fixture()
async def admin_registered_user(async_client: AsyncClient, fastapi_dep) -> dict:
    user_details = {
        "email": "test_admin@example.net",
        "password": "1234",
        "is_admin": True,
    }

    with fastapi_dep(app).override({is_user_admin: lambda: True}):
        await async_client.post("/register", json=user_details)

    query = users_table.select().where(users_table.c.email == user_details["email"])
    user = await database.fetch_one(query)

    user_details["id"] = user.id
    return user_details


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.net", "password": "1234", "is_admin": False}
    await async_client.post("/register", json=user_details)
    query = users_table.select().where(users_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, registered_user: dict) -> str:
    response = await async_client.post("/token", json=registered_user)
    return response.json()["access_token"]


@pytest.fixture()
async def logged_in_admin_token(
    async_client: AsyncClient, admin_registered_user: dict
) -> str:
    response = await async_client.post("/token", json=admin_registered_user)
    return response.json()["access_token"]
