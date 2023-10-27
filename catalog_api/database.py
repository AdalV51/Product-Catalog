import datetime

import databases
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)

from catalog_api.config import config

metadata = MetaData()


products_table = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("sku", String, unique=True, nullable=False),
    Column("price", Float, nullable=False),
    Column("brand", String, nullable=False),
)


users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("password", String),
    Column("is_admin", Boolean, default=False),
)


product_analytics_table = Table(
    "product_analytics",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), nullable=False),
    Column("view_date", DateTime, default=datetime.datetime.utcnow, nullable=False),
)

action_enum = Enum("ADDED", "UPDATED", "DELETED", name="action_enum")

audit_log_table = Table(
    "audit_log",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), nullable=False),
    Column("action", action_enum, nullable=False),
    Column("previous_data", String, nullable=True),
    Column("new_data", String, nullable=True),
    Column("changed_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("timestamp", DateTime, default=datetime.datetime.utcnow, nullable=False),
)

engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)
