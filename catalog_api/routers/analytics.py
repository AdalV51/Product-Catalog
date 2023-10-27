from typing import List, Optional

from fastapi import APIRouter, Query, status

from catalog_api.database import database
from catalog_api.models.analytics import ProductViewCount

router = APIRouter()


@router.get(
    "/product-views/",
    response_model=List[ProductViewCount],
    status_code=status.HTTP_200_OK,
)
async def get_products_views():
    query = "SELECT product_id, COUNT(*) AS count FROM product_analytics GROUP BY product_id"
    return await database.fetch_all(query)


@router.get(
    "/product-views/{product_id}",
    response_model=ProductViewCount,
    status_code=status.HTTP_200_OK,
)
async def get_specific_product_views(product_id: int):
    query = f"SELECT product_id, COUNT(*) AS count FROM product_analytics WHERE product_id = {product_id} GROUP BY product_id"
    views = await database.fetch_one(query)
    print(views)
    if not views:
        return {"product_id": product_id, "count": 0}
    return views


@router.get(
    "/product-views/filter/",
    response_model=List[ProductViewCount],
    status_code=status.HTTP_200_OK,
)
async def get_product_views_filtered(
    month: Optional[int] = Query(None, ge=1, le=12), year: Optional[int] = Query(None)
):
    """
    Read product views by a specific month and year
    :param month: Month to filter (1-12)
    :param year: Year to filter
    """

    # Base part of the query
    query = "SELECT product_id, COUNT(*) AS count FROM product_analytics"

    # List to hold where conditions
    conditions = []

    if year:
        conditions.append(f"strftime('%Y', view_date) = '{year}'")
    if month:
        conditions.append(f"strftime('%m', view_date) = '{str(month).zfill(2)}'")

    # If any conditions exist, append them to the query
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY product_id"

    return await database.fetch_all(query)
