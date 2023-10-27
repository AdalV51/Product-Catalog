from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from catalog_api.database import database
from catalog_api.reports.product_changes import send_daily_report
from catalog_api.routers.analytics import router as product_analytics_router
from catalog_api.routers.products import router as products_router
from catalog_api.routers.users import router as users_router
from catalog_api.security import create_default_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await create_default_admin()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(products_router)
app.include_router(product_analytics_router)
app.include_router(users_router)

scheduler = AsyncIOScheduler()
scheduler.add_job(send_daily_report, "interval", minutes=1)
# scheduler.add_job(send_daily_report, "interval", days=1)
scheduler.start()
