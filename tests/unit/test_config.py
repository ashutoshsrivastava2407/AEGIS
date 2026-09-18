"""Unit Tests for AEGIS Settings Configuration."""

from packages.config import settings


def test_settings_defaults():
    assert settings.AEGIS_ENV == "development"
    assert settings.API_PORT == 8000
    assert settings.POSTGRES_PORT == 5432
    assert settings.REDIS_PORT == 6379
    assert settings.DEFAULT_TENANT_ID == "00000000-0000-0000-0000-000000000001"
