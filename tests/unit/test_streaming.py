"""AEGIS Real-Time Streaming Subsystem Unit Tests."""

import os
import pytest
from packages.events.envelope import EventEnvelope
from packages.events.schema_registry import SchemaRegistry, SchemaValidationError
from services.streaming.broker import (
    InMemoryEventBroker,
    KafkaEventBroker,
    BrokerUnavailableError,
    get_event_broker,
)
from services.streaming.idempotency.store import IdempotencyStore
from services.streaming.producers.event_producer import EventProducer


def test_event_envelope_creation_and_dict():
    """Verify EventEnvelope instantiation and serialization."""
    env = EventEnvelope(
        event_type="order.created",
        tenant_id="tenant-alpha",
        source="checkout_service",
        entity_type="order",
        entity_id="ORD-1001",
        payload={"amount": 99.99, "currency": "USD"},
    )
    d = env.to_dict()
    assert d["event_type"] == "order.created"
    assert d["tenant_id"] == "tenant-alpha"
    assert d["payload"]["amount"] == 99.99
    assert env.event_id is not None


def test_schema_registry_validation():
    """Verify schema registration and payload validation rules."""
    registry = SchemaRegistry()
    registry.register_schema(
        event_type="user.signed_up",
        schema_version="1.0",
        required_fields=["user_id", "email"],
        field_types={"email": "string", "user_id": "string"},
    )

    # Valid event
    valid_env = EventEnvelope(
        event_type="user.signed_up",
        schema_version="1.0",
        tenant_id="t1",
        source="web",
        entity_type="user",
        entity_id="U-1",
        payload={"user_id": "U-1", "email": "user@aegis.ai"},
    )
    assert registry.validate(valid_env) is True

    # Invalid event missing field
    invalid_env = EventEnvelope(
        event_type="user.signed_up",
        schema_version="1.0",
        tenant_id="t1",
        source="web",
        entity_type="user",
        entity_id="U-2",
        payload={"user_id": "U-2"},  # missing email
    )
    with pytest.raises(SchemaValidationError) as exc_info:
        registry.validate(invalid_env)
    assert "email" in str(exc_info.value)


def test_idempotency_store():
    """Verify duplicate event detection and TTL store."""
    store = IdempotencyStore(ttl_seconds=60)
    tenant_id = "tenant-beta"
    event_id = "evt-999"

    assert store.is_duplicate(tenant_id, event_id) is False
    store.mark_processed(tenant_id, event_id)
    assert store.is_duplicate(tenant_id, event_id) is True
    assert store.is_duplicate(tenant_id, "evt-1000") is False


def test_production_broker_mode_enforcement(monkeypatch):
    """Verify production Kafka broker rule:
    - In-memory broker raises BrokerUnavailableError if created outside test mode.
    - get_event_broker raises BrokerUnavailableError when Kafka broker is unreachable rather than silently falling back.
    """
    # 1. Direct instantiation of InMemoryEventBroker outside test env without flag must fail
    monkeypatch.setenv("AEGIS_ENV", "production")
    monkeypatch.setenv("ALLOW_IN_MEMORY_BROKER", "false")
    with pytest.raises(BrokerUnavailableError) as exc_info:
        InMemoryEventBroker(is_test_environment=False)
    assert "InMemoryEventBroker is permitted ONLY inside isolated unit tests" in str(exc_info.value)

    # 2. In production mode with unconfigured Kafka, get_event_broker fails fast
    monkeypatch.setenv("AEGIS_BROKER_TYPE", "kafka")
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "")
    monkeypatch.setenv("AEGIS_KAFKA_SIMULATION", "false")
    with pytest.raises(BrokerUnavailableError) as exc_info2:
        get_event_broker(force_test_broker=False)
    assert "Production Kafka broker is unavailable" in str(exc_info2.value)


@pytest.mark.asyncio
async def test_event_producer_publish():
    """Verify EventProducer publishes envelopes to broker."""
    broker = InMemoryEventBroker(is_test_environment=True)
    registry = SchemaRegistry()
    producer = EventProducer(broker=broker, schema_registry=registry)

    env = EventEnvelope(
        event_type="telemetry.ping",
        tenant_id="tenant-gamma",
        source="sensor_01",
        entity_type="sensor",
        entity_id="SNS-88",
        payload={"value": 42.0},
    )

    receipt = await producer.send("sensors.v1", env)
    assert receipt["status"] == "DELIVERED"
    assert receipt["topic"] == "sensors.v1"
