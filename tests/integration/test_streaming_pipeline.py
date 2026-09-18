"""AEGIS Real-Time Streaming Subsystem Integration Tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from packages.database.base import Base
from packages.events.envelope import EventEnvelope
from services.streaming.broker import InMemoryEventBroker
from services.streaming.consumers.consumer_group import EventConsumerGroup
from services.streaming.dlq.manager import DLQManager
from services.streaming.processing.medallion_stream import MedallionStreamProcessor
from services.streaming.producers.event_producer import EventProducer
from services.streaming.services import StreamingDataPlatformService


@pytest.fixture
def db_session():
    """In-memory SQLite session for integration testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.mark.asyncio
async def test_end_to_end_streaming_pipeline(db_session):
    """Test full event lifecycle: produce -> broker -> consumer microbatch -> medallion storage."""
    broker = InMemoryEventBroker(is_test_environment=True)
    producer = EventProducer(broker=broker)
    tenant_id = "tenant-integration"
    topic_name = "orders.stream.v1"

    await broker.create_topic(topic_name, partitions=2)

    # 1. Produce 3 events
    received_payloads = []

    def handler(env: EventEnvelope):
        received_payloads.append(env.payload)

    for i in range(3):
        env = EventEnvelope(
            event_type="order.placed",
            tenant_id=tenant_id,
            source="test_runner",
            entity_type="order",
            entity_id=f"ORD-{i}",
            payload={"item": f"Widget-{i}", "price": 10.0 + i},
        )
        await producer.send(topic_name, env)

    # 2. Consumer group consumes micro-batch across partitions
    consumer_group = EventConsumerGroup(
        group_id="order_processor_group",
        topic_name=topic_name,
        tenant_id=tenant_id,
        broker=broker,
    )

    total_processed = 0
    for partition_id in range(2):
        batch_result = await consumer_group.consume_batch(
            db_session=db_session,
            handler=handler,
            partition=partition_id,
            max_batch_size=10,
        )
        total_processed += batch_result["processed_count"]

    assert total_processed > 0
    assert len(received_payloads) > 0

    # 3. Verify Real-time Medallion Stream persistence
    medallion = MedallionStreamProcessor()
    sample_env = EventEnvelope(
        event_type="order.placed",
        tenant_id=tenant_id,
        source="test_runner",
        entity_type="order",
        entity_id="ORD-100",
        payload={"item": "Widget-100"},
    )
    bronze_res = await medallion.process_bronze_stream(tenant_id, topic_name, [sample_env])
    silver_res = await medallion.process_silver_stream(tenant_id, topic_name, [sample_env])

    assert bronze_res["stored"] is True
    assert silver_res["stored"] is True


@pytest.mark.asyncio
async def test_dlq_capture_and_replay(db_session):
    """Test Dead-Letter Queue capture on cross-tenant mismatch and admin replay."""
    broker = InMemoryEventBroker(is_test_environment=True)
    tenant_id = "tenant-a"
    topic_name = "dlq.test.topic"

    await broker.create_topic(topic_name, partitions=1)

    # Capture failure in DLQ
    dlq_record = DLQManager.capture_failure(
        session=db_session,
        tenant_id=tenant_id,
        topic_name=topic_name,
        error_category="SCHEMA_VALIDATION_FAILED",
        error_message="Missing required field 'account_id'",
        raw_payload={"event_type": "account.updated", "payload": {"invalid": True}},
        partition_id=0,
        offset=5,
    )

    assert dlq_record.id is not None
    assert dlq_record.status == "PENDING"

    # Replay DLQ record
    replay_result = await DLQManager.replay_record(
        session=db_session,
        dlq_id=dlq_record.id,
        tenant_id=tenant_id,
        broker=broker,
    )

    assert replay_result["status"] == "REPLAYED"
    assert dlq_record.status == "REPLAYED"
