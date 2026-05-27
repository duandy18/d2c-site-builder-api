from app.core.config import get_settings


def test_settings_load() -> None:
    settings = get_settings()

    assert settings.service_name == "d2c-site-builder-api"
    assert settings.environment
