import pytest
from httpx import AsyncClient


async def create_product(
    body: dict, async_client: AsyncClient, logged_in_admin_token: str
) -> dict:
    response = await async_client.post(
        "/products",
        json=body,
        headers={"Authorization": f"Bearer {logged_in_admin_token}"},
    )
    return response.json()


@pytest.fixture()
async def created_product(async_client: AsyncClient, logged_in_admin_token: str):
    product_data = {
        "name": "New Product",
        "sku": "1234567890",
        "price": 99.9,
        "brand": "Luuna",
    }
    return await create_product(product_data, async_client, logged_in_admin_token)


@pytest.mark.anyio
async def test_get_products(async_client: AsyncClient, created_product: dict):
    response = await async_client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "New Product"
    assert response.json()[0]["sku"] == "1234567890"
    assert response.json()[0]["price"] == 99.9
    assert response.json()[0]["brand"] == "Luuna"


@pytest.mark.anyio
async def test_get_product(async_client: AsyncClient, created_product: dict):
    response = await async_client.get(f"/products/{created_product['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == created_product["name"]
    assert response.json()["sku"] == created_product["sku"]
    assert response.json()["price"] == created_product["price"]
    assert response.json()["brand"] == created_product["brand"]


@pytest.mark.anyio
async def test_create_product(
    async_client: AsyncClient,
    logged_in_admin_token: str,
):
    new_product = {
        "name": "New Product",
        "sku": "1234567890",
        "price": 99.9,
        "brand": "Luuna",
    }

    response = await async_client.post(
        "/products",
        json=new_product,
        headers={"Authorization": f"Bearer {logged_in_admin_token}"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == new_product["name"]
    assert response.json()["sku"] == new_product["sku"]
    assert response.json()["price"] == new_product["price"]
    assert response.json()["brand"] == new_product["brand"]


@pytest.mark.anyio
async def test_non_admin_create_product(
    async_client: AsyncClient,
    logged_in_token: str,
):
    new_product = {
        "name": "New Product",
        "sku": "1234567890",
        "price": 99.9,
        "brand": "Luuna",
    }

    response = await async_client.post(
        "/products",
        json=new_product,
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Only admin can access this"


@pytest.mark.anyio
async def test_create_product_repeated_sku(
    async_client: AsyncClient,
    logged_in_admin_token: str,
    created_product: dict,
):
    new_product = {
        "name": "Product with repeated SKU",
        "sku": "1234567890",
        "price": 66.6,
        "brand": "Mappa",
    }

    response = await async_client.post(
        "/products",
        json=new_product,
        headers={"Authorization": f"Bearer {logged_in_admin_token}"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "SKU already exist"


@pytest.mark.anyio
async def test_put_product(
    async_client: AsyncClient, logged_in_admin_token: str, created_product: dict
):
    product_changes = {
        "name": "Updated PUT Product",
        "sku": "0123456789",
        "price": 33.3,
        "brand": "Mappa",
    }

    response = await async_client.put(
        f"/products/{created_product['id']}",
        json=product_changes,
        headers={"Authorization": f"Bearer {logged_in_admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == product_changes["name"]
    assert response.json()["sku"] == product_changes["sku"]
    assert response.json()["price"] == product_changes["price"]
    assert response.json()["brand"] == product_changes["brand"]


@pytest.mark.anyio
async def test_non_admin_put_product(
    async_client: AsyncClient, logged_in_token: str, created_product: dict
):
    product_changes = {
        "name": "Updated PUT Product",
        "sku": "0123456789",
        "price": 33.3,
        "brand": "Mappa",
    }

    response = await async_client.put(
        f"/products/{created_product['id']}",
        json=product_changes,
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Only admin can access this"


@pytest.mark.anyio
async def test_patch_product(
    async_client: AsyncClient, logged_in_admin_token: str, created_product: dict
):
    product_changes = {
        "sku": "12301230123",
    }

    response = await async_client.patch(
        f"/products/{created_product['id']}",
        json=product_changes,
        headers={"Authorization": f"Bearer {logged_in_admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == created_product["name"]
    assert response.json()["sku"] == product_changes["sku"]
    assert response.json()["price"] == created_product["price"]
    assert response.json()["brand"] == created_product["brand"]


@pytest.mark.anyio
async def test_non_admin_patch_product(
    async_client: AsyncClient, logged_in_token: str, created_product: dict
):
    product_changes = {
        "sku": "12301230123",
    }

    response = await async_client.patch(
        f"/products/{created_product['id']}",
        json=product_changes,
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Only admin can access this"


@pytest.mark.anyio
async def test_delete_product(
    async_client: AsyncClient, logged_in_admin_token: str, created_product: dict
):
    response = await async_client.delete(
        f"/products/{created_product['id']}",
        headers={"Authorization": f"Bearer {logged_in_admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Product deleted sucessfully"


@pytest.mark.anyio
async def test_non_admin_delete_product(
    async_client: AsyncClient, logged_in_token: str, created_product: dict
):
    response = await async_client.delete(
        f"/products/{created_product['id']}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Only admin can access this"
