"""AEGIS Event Producer.

Validates event schemas, enriches envelopes, and publishes to streaming event broker.
"""

import logging
from typing import Any, Dict, Optional
from packages.events.envelope import EventEnvelope
from packages.events.schema_registry import SchemaRegistry, global_schema_registry, SchemaValidationError
from services.streaming.broker import EventBroker

logger = logging.getLogger("aegis.streaming.producer")


class EventProducer:
    """Production Event Producer with schema validation and delivery ACK."""

    def __init__(self, broker: EventBroker, schema_registry: Optional[SchemaRegistry] = None):
        self.broker = broker
        self.schema_registry = schema_registry or global_schema_registry

    async def send(
        self,
        topic_name: str,
        envelope: EventEnvelope,
        partition_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate envelope against SchemaRegistry and publish to broker topic."""
        # 1. Tenant ID validation
        if not envelope.tenant_id:
            raise ValueError("EventEnvelope tenant_id is required for multi-tenant boundary security.")

        # 2. Schema Validation
        try:
            self.schema_registry.validate(envelope)
        except SchemaValidationError as e:
            logger.error(
                "Schema validation failed for event_id=%s, event_type=%s: %s",
                envelope.event_id, envelope.event_type, str(e)
            )
            raise

        # 3. Publish to Broker
        key = partition_key or envelope.entity_id or envelope.event_id
        receipt = await self.broker.publish(topic_name, envelope, partition_key=key)

        logger.info(
            "Event produced successfully event_id=%s topic=%s partition=%d offset=%d",
            envelope.event_id, topic_name, receipt["partition"], receipt["offset"]
        )

        return receipt
