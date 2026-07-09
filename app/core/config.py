import os
from functools import lru_cache

from pydantic import BaseModel


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


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
    cors_origins: list[str] = _split_csv(
        os.getenv(
            "D2C_SITE_BUILDER_CORS_ORIGINS",
            ",".join(
                [
                    "http://localhost:5299",
                    "http://127.0.0.1:5299",
                    "http://localhost:5301",
                    "http://127.0.0.1:5301",
                    "http://192.168.1.3:5299",
                    "http://100.117.111.7:5299",
                ]
            ),
        )
    )
    service_name: str = "d2c-site-builder-api"
    d2c_api_base_url: str = os.getenv("D2C_API_BASE_URL", "http://127.0.0.1:8025")
    d2c_api_timeout_seconds: float = float(os.getenv("D2C_API_TIMEOUT_SECONDS", "5"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
