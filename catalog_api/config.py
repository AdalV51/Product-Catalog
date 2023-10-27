from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings, extra="allow"):
    ENV_STATE: Optional[str] = None

    """Loads the dotenv file. Including this is necessary to get
    pydantic to load a .env file."""
    model_config = SettingsConfigDict(env_file=".env")


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    DB_ADMIN_EMAIL: Optional[str] = None
    DB_ADMIN_PWD: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True
    DB_ADMIN_EMAIL: str = "admin_test@test.com"
    DB_ADMIN_PWD: str = "admin_test"
    SECRET_KEY: Optional[str] = "V3OwumLWmf3DPijohTNBWYUYQFqE7wDV3SoW8Ri0o0c="
    ALGORITHM: Optional[str] = "HS256"

    model_config = SettingsConfigDict(env_prefix="TEST_")


@lru_cache()
def get_config(env_state: str):
    """Instantiate config based on the environment."""
    configs = {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
