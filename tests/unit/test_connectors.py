"""Unit Tests for AEGIS Data Connectors (CSV, JSON, PostgreSQL, REST)."""

import pytest
from services.data_platform.connectors import (
    csv_connector,
    json_connector,
    postgres_connector,
    rest_connector,
)


@pytest.mark.asyncio
async def test_csv_connector_read_and_schema():
    config = {
        "file_path": "data/fixtures/valid_orders.csv",
        "delimiter": ",",
    }
    valid, msg = csv_connector.validate_config(config)
    assert valid is True

    records = await csv_connector.read(config)
    assert len(records) == 5
    assert records[0]["order_id"] == "ord_1001"
    assert records[0]["amount"] == 249.99

    schema = await csv_connector.discover_schema(config)
    assert "columns" in schema
    assert len(schema["columns"]) == 5


@pytest.mark.asyncio
async def test_json_connector_read():
    config = {
        "file_path": "data/fixtures/sample_events.json",
    }
    records = await json_connector.read(config)
    assert len(records) == 3
    assert records[0]["event_type"] == "USER_SIGNUP"


@pytest.mark.asyncio
async def test_postgres_connector():
    config = {
        "host": "localhost",
        "port": 5432,
        "database": "aegis_db",
        "user": "aegis_app",
        "table_name": "users",
    }
    ok, msg = await postgres_connector.test_connection(config)
    assert ok is True

    records = await postgres_connector.read(config)
    assert len(records) > 0


@pytest.mark.asyncio
async def test_rest_connector():
    config = {
        "endpoint_url": "https://api.github.com/events",
        "method": "GET",
    }
    ok, msg = await rest_connector.test_connection(config)
    assert ok is True
