"""AEGIS Real-Time Streaming Subsystem Package."""

from services.streaming.broker import (
    EventBroker,
    KafkaEventBroker,
    InMemoryEventBroker,
    BrokerUnavailableError,
    get_event_broker,
)
from services.streaming.producers.event_producer import EventProducer
from services.streaming.consumers.consumer_group import EventConsumerGroup
from services.streaming.idempotency.store import IdempotencyStore
from services.streaming.dlq.manager import DLQManager
from services.streaming.quality.evaluator import StreamQualityEvaluator
from services.streaming.processing.medallion_stream import MedallionStreamProcessor
from services.streaming.services import StreamingDataPlatformService

__all__ = [
    "EventBroker",
    "KafkaEventBroker",
    "InMemoryEventBroker",
    "BrokerUnavailableError",
    "get_event_broker",
    "EventProducer",
    "EventConsumerGroup",
    "IdempotencyStore",
    "DLQManager",
    "StreamQualityEvaluator",
    "MedallionStreamProcessor",
    "StreamingDataPlatformService",
]
