"""AEGIS Event Consumer Group Manager.

Partition consumer group executor handling deserialization, deduplication, partition offset commits, and DLQ routing.
"""

import asyncio
import inspect
from datetime import datetime, timezone
import logging
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy.orm import Session

from packages.database.models.stream_consumer import StreamConsumerGroupModel, StreamPartitionOffsetModel
from packages.events.envelope import EventEnvelope
from services.streaming.broker import EventBroker
from services.streaming.dlq.manager import DLQManager
from services.streaming.idempotency.store import IdempotencyStore, global_idempotency_store

logger = logging.getLogger("aegis.streaming.consumer")


class EventConsumerGroup:
    """Consumer Group partition processing engine."""

    def __init__(
        self,
        group_id: str,
        topic_name: str,
        tenant_id: str,
        broker: EventBroker,
        idempotency_store: Optional[IdempotencyStore] = None
    ):
        self.group_id = group_id
        self.topic_name = topic_name
        self.tenant_id = tenant_id
        self.broker = broker
        self.idempotency_store = idempotency_store or global_idempotency_store

    async def consume_batch(
        self,
        db_session: Session,
        handler: Callable[[EventEnvelope], Any],
        partition: int = 0,
        max_batch_size: int = 50
    ) -> Dict[str, Any]:
        """Poll and execute a micro-batch of messages from topic partition."""
        # 1. Fetch current offset state from DB
        group_model = (
            db_session.query(StreamConsumerGroupModel)
            .filter(
                StreamConsumerGroupModel.tenant_id == self.tenant_id,
                StreamConsumerGroupModel.group_id == self.group_id,
                StreamConsumerGroupModel.topic_name == self.topic_name
            )
            .first()
        )

        if not group_model:
            group_model = StreamConsumerGroupModel(
                tenant_id=self.tenant_id,
                group_id=self.group_id,
                topic_name=self.topic_name,
                state="STABLE",
                members_count=1,
                total_lag=0
            )
            db_session.add(group_model)
            db_session.commit()
            db_session.refresh(group_model)

        offset_model = (
            db_session.query(StreamPartitionOffsetModel)
            .filter(
                StreamPartitionOffsetModel.consumer_group_id == group_model.id,
                StreamPartitionOffsetModel.partition_id == partition
            )
            .first()
        )

        current_offset = offset_model.current_offset if offset_model else 0

        # 2. Read messages from broker
        messages = await self.broker.get_messages(
            self.topic_name,
            partition=partition,
            offset=current_offset,
            limit=max_batch_size
        )

        if not messages:
            return {
                "group_id": self.group_id,
                "topic": self.topic_name,
                "partition": partition,
                "processed_count": 0,
                "skipped_duplicates": 0,
                "failed_dlq": 0,
            }

        processed_count = 0
        skipped_duplicates = 0
        failed_dlq = 0
        new_offset = current_offset

        for msg in messages:
            raw_env = msg.get("envelope", {})
            msg_offset = msg.get("offset", new_offset)

            try:
                envelope = EventEnvelope.from_dict(raw_env)
                
                # Check Tenant boundary
                if envelope.tenant_id != self.tenant_id:
                    logger.warning("Rejecting event with cross-tenant boundary mismatch event_id=%s", envelope.event_id)
                    DLQManager.capture_failure(
                        session=db_session,
                        tenant_id=self.tenant_id,
                        topic_name=self.topic_name,
                        error_category="CONTRACT_VIOLATION",
                        error_message="Cross-tenant isolation policy violation",
                        raw_payload=raw_env,
                        partition_id=partition,
                        offset=msg_offset,
                        event_id=envelope.event_id,
                    )
                    failed_dlq += 1
                    new_offset = msg_offset + 1
                    continue

                # Idempotency deduplication check
                if self.idempotency_store.is_duplicate(self.tenant_id, envelope.event_id):
                    logger.info("Skipping duplicate event_id=%s for group=%s", envelope.event_id, self.group_id)
                    skipped_duplicates += 1
                    new_offset = msg_offset + 1
                    continue

                # Execute handler
                if inspect.iscoroutinefunction(handler):
                    await handler(envelope)
                else:
                    handler(envelope)

                # Mark processed in idempotency store
                self.idempotency_store.mark_processed(self.tenant_id, envelope.event_id)
                processed_count += 1
                new_offset = msg_offset + 1

            except Exception as ex:
                logger.error("Consumer error processing offset %d: %s", msg_offset, str(ex))
                DLQManager.capture_failure(
                    session=db_session,
                    tenant_id=self.tenant_id,
                    topic_name=self.topic_name,
                    error_category="PROCESSOR_EXCEPTION",
                    error_message=str(ex),
                    raw_payload=raw_env,
                    partition_id=partition,
                    offset=msg_offset,
                    exception=ex,
                )
                failed_dlq += 1
                new_offset = msg_offset + 1

        # 3. Update offset checkpoint in database
        topic_offsets = await self.broker.get_topic_offsets(self.topic_name)
        log_end_offset = topic_offsets.get(partition, new_offset)
        lag = max(0, log_end_offset - new_offset)

        if not offset_model:
            offset_model = StreamPartitionOffsetModel(
                tenant_id=self.tenant_id,
                consumer_group_id=group_model.id,
                topic_name=self.topic_name,
                partition_id=partition,
                current_offset=new_offset,
                log_end_offset=log_end_offset,
                lag=lag,
            )
            db_session.add(offset_model)
        else:
            offset_model.current_offset = new_offset
            offset_model.log_end_offset = log_end_offset
            offset_model.lag = lag

        # Update total group lag
        all_offsets = (
            db_session.query(StreamPartitionOffsetModel)
            .filter(StreamPartitionOffsetModel.consumer_group_id == group_model.id)
            .all()
        )
        group_model.total_lag = sum(o.lag for o in all_offsets)
        group_model.updated_at = datetime.now(timezone.utc)

        db_session.commit()

        return {
            "group_id": self.group_id,
            "topic": self.topic_name,
            "partition": partition,
            "processed_count": processed_count,
            "skipped_duplicates": skipped_duplicates,
            "failed_dlq": failed_dlq,
            "current_offset": new_offset,
            "lag": lag,
        }
