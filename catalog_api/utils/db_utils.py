import datetime

from catalog_api.database import audit_log_table, database, product_analytics_table


async def add_product_anonymous_view(product_id: int):
    query = product_analytics_table.insert().values(
        {"product_id": product_id, "view_date": datetime.datetime.utcnow()}
    )
    await database.execute(query)


async def add_audit_entry(data: dict):
    query = audit_log_table.insert().values(
        {**data, "timestamp": datetime.datetime.utcnow()}
    )
    await database.execute(query)
