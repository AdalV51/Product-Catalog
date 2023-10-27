import pytest
from httpx import AsyncClient

from catalog_api.main import app
from catalog_api.security import get_current_user, get_user, is_user_admin


async def register_user(
    async_client: AsyncClient, email: str, password: str, is_admin: bool
):
    return await async_client.post(
        "/register", json={"email": email, "password": password, "is_admin": is_admin}
    )


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test1@example.net", "1234", False)
    assert response.status_code == 201
    assert "User created successfully" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_admin_user(async_client: AsyncClient, fastapi_dep):
    with fastapi_dep(app).override({is_user_admin: lambda: True}):
        response = await register_user(async_client, "test1@example.net", "1234", True)

    assert response.status_code == 201
    assert "User created successfully" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_admin_user_from_non_admin(async_client: AsyncClient):
    response = await register_user(async_client, "test1@example.net", "1234", True)

    assert response.status_code == 403
    assert response.json()["detail"] == "Only admin users can create admin users"


@pytest.mark.anyio
async def test_register_user_already_exists(
    async_client: AsyncClient, registered_user: dict
):
    response = await register_user(
        async_client, registered_user["email"], registered_user["password"], False
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/token", json={"email": "test@example.net", "password": "1234"}
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "/token",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_login_admin_user(async_client: AsyncClient, admin_credentials: dict):
    response = await async_client.post(
        "/token",
        json=admin_credentials,
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_patch_user(
    async_client: AsyncClient,
    registered_user: dict,
    admin_credentials: dict,
    fastapi_dep,
):
    user_details = {
        "email": "new_test@example.net",
        "is_admin": True,
    }

    user = await get_user(email=admin_credentials["email"])

    with fastapi_dep(app).override({get_current_user: lambda: user}):
        response = await async_client.patch(
            f"/user/{registered_user['id']}", json=user_details
        )

    assert response.status_code == 200
    assert response.json()["email"] == user_details["email"]
    assert response.json()["is_admin"] == user_details["is_admin"]


@pytest.mark.anyio
async def test_delete_user(
    async_client: AsyncClient,
    registered_user: dict,
    admin_credentials: dict,
    fastapi_dep,
):
    user = await get_user(email=admin_credentials["email"])

    with fastapi_dep(app).override({get_current_user: lambda: user}):
        response = await async_client.delete(f"/user/{registered_user['id']}")

    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted sucessfully"


@pytest.mark.anyio
async def test_admin_user(admin_registered_user: dict):
    assert admin_registered_user["is_admin"] is True
