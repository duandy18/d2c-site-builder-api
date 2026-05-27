import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    environment: str = os.getenv("D2C_SITE_BUILDER_ENVIRONMENT", "local")
    database_url: str = os.getenv(
        "D2C_SITE_BUILDER_DATABASE_URL",
        "postgresql+psycopg://d2c_site_builder:d2c_site_builder@127.0.0.1:5433/d2c_site_builder",
    )
    test_database_url: str = os.getenv(
        "D2C_SITE_BUILDER_TEST_DATABASE_URL",
        "postgresql+psycopg://d2c_site_builder:d2c_site_builder@127.0.0.1:5433/d2c_site_builder_test",
    )
    service_name: str = "d2c-site-builder-api"


@lru_cache
def get_settings() -> Settings:
    return Settings()
