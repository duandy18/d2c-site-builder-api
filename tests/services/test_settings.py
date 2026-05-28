from app.core.config import get_settings


def test_settings_load() -> None:
    settings = get_settings()

    assert settings.service_name == "d2c-site-builder-api"
    assert settings.environment


def test_settings_include_local_preview_web_cors_origin() -> None:
    settings = get_settings()

    assert "http://localhost:5301" in settings.cors_origins
    assert "http://127.0.0.1:5301" in settings.cors_origins
