import json
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from catalog_api.database import database, products_table
from catalog_api.models.products import (
    Product,
    ProductCreate,
    ProductPatchResponse,
    ProductUpdatePatch,
    ProductUpdatePut,
)
from catalog_api.models.users import User
from catalog_api.security import get_current_user, is_user_valid
from catalog_api.utils.db_utils import add_audit_entry, add_product_anonymous_view

router = APIRouter()


@router.get("/products", response_model=List[Product], status_code=status.HTTP_200_OK)
async def read_products():
    query = products_table.select()
    return await database.fetch_all(query)


@router.get(
    "/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK
)
async def read_product(
    product_id: int,
    is_valid_user: Annotated[bool, Depends(is_user_valid)],
):
    query = products_table.select().where(products_table.c.id == product_id)
    product = await database.fetch_one(query)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    if not is_valid_user:
        await add_product_anonymous_view(product_id)

    return product


@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate, current_user: Annotated[User, Depends(get_current_user)]
):
    data = product.dict()
    existing_sku_query = products_table.select().where(
        products_table.c.sku == product.sku
    )
    if await database.fetch_one(existing_sku_query):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="SKU already exist"
        )

    query = products_table.insert().values(data)

    last_record_id = await database.execute(query)
    new_record = {**data, "id": last_record_id}

    await add_audit_entry(
        data={
            "product_id": new_record["id"],
            "action": "ADDED",
            "previous_data": None,
            "new_data": json.dumps(new_record),
            "changed_by": current_user.id,
        }
    )

    return new_record


@router.put(
    "/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK
)
async def complete_update_product(
    product: ProductUpdatePut,
    product_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    data = product.dict()
    previous_data = await read_product(product_id, is_valid_user=True)
    query = (
        products_table.update().where(products_table.c.id == product_id).values(data)
    )
    last_record_id = await database.execute(query)
    if not last_record_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    updated_record = {**data, "id": last_record_id}

    await add_audit_entry(
        data={
            "product_id": updated_record["id"],
            "action": "UPDATED",
            "previous_data": json.dumps(dict(previous_data)),
            "new_data": json.dumps(dict(updated_record)),
            "changed_by": current_user.id,
        }
    )

    return updated_record


@router.patch(
    "/products/{product_id}",
    response_model=ProductPatchResponse,
    status_code=status.HTTP_200_OK,
)
async def partially_update_product(
    product: ProductUpdatePatch,
    product_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    data = product.dict(exclude_unset=True)
    previous_data = await read_product(product_id, is_valid_user=True)
    query = (
        products_table.update().where(products_table.c.id == product_id).values(data)
    )
    last_record_id = await database.execute(query)
    if not last_record_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    new_data = await read_product(product_id, is_valid_user=True)

    await add_audit_entry(
        data={
            "product_id": new_data["id"],
            "action": "UPDATED",
            "previous_data": json.dumps(dict(previous_data)),
            "new_data": json.dumps(dict(new_data)),
            "changed_by": current_user.id,
        }
    )

    return new_data


@router.delete("/products/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    previous_data = await read_product(product_id, is_valid_user=True)
    query = products_table.delete().where(products_table.c.id == product_id)
    product = await database.execute(query)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    await add_audit_entry(
        data={
            "product_id": previous_data["id"],
            "action": "DELETED",
            "previous_data": json.dumps(dict(previous_data)),
            "new_data": None,
            "changed_by": current_user.id,
        }
    )

    return {"detail": "Product deleted sucessfully"}
