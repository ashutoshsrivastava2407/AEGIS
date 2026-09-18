"""AEGIS Dead-Letter Queue (DLQ) Manager & Replay Engine.

Routes unprocessable, malformed, or failed streaming events to DLQ storage and provides admin replay capabilities.
"""

from datetime import datetime, timezone
import logging
import traceback
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from packages.database.models.dlq_record import DLQRecordModel
from packages.events.envelope import EventEnvelope
from services.streaming.broker import EventBroker

logger = logging.getLogger("aegis.streaming.dlq")


class DLQManager:
    """Dead-Letter Queue router and replay executor."""

    @staticmethod
    def capture_failure(
        session: Session,
        tenant_id: str,
        topic_name: str,
        error_category: str,
        error_message: str,
        raw_payload: Dict[str, Any],
        partition_id: int = 0,
        offset: int = 0,
        event_id: Optional[str] = None,
        exception: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DLQRecordModel:
        """Persist a failed event into the Dead-Letter Queue."""
        tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__)) if exception else None

        dlq_record = DLQRecordModel(
            tenant_id=tenant_id,
            event_id=event_id,
            topic_name=topic_name,
            partition_id=partition_id,
            offset=offset,
            error_category=error_category,
            error_message=error_message,
            stack_trace=tb,
            raw_payload=raw_payload or {},
            metadata_json=metadata or {},
            retry_count=0,
            status="PENDING",
        )
        session.add(dlq_record)
        session.commit()
        session.refresh(dlq_record)

        logger.warning(
            "Captured DLQ record id=%s tenant=%s topic=%s category=%s error=%s",
            dlq_record.id, tenant_id, topic_name, error_category, error_message
        )
        return dlq_record

    @staticmethod
    async def replay_record(
        session: Session,
        dlq_id: str,
        tenant_id: str,
        broker: EventBroker
    ) -> Dict[str, Any]:
        """Replay a DLQ record by re-publishing its payload back into the source stream topic."""
        dlq_record = (
            session.query(DLQRecordModel)
            .filter(DLQRecordModel.id == dlq_id, DLQRecordModel.tenant_id == tenant_id)
            .first()
        )
        if not dlq_record:
            raise ValueError(f"DLQ Record id='{dlq_id}' not found for tenant '{tenant_id}'")

        if dlq_record.status == "REPLAYED":
            raise ValueError(f"DLQ Record id='{dlq_id}' has already been replayed.")

        # Reconstruct or parse envelope
        payload = dlq_record.raw_payload
        envelope = EventEnvelope(
            event_id=dlq_record.event_id or f"replay-{dlq_record.id}",
            event_type=payload.get("event_type", "replayed.event"),
            event_version=payload.get("event_version", "1.0.0"),
            tenant_id=tenant_id,
            source=payload.get("source", "dlq.replay"),
            entity_type=payload.get("entity_type", "dlq_record"),
            entity_id=payload.get("entity_id", dlq_record.id),
            payload=payload.get("payload", payload),
            metadata={"replayed_from_dlq_id": dlq_record.id, **dlq_record.metadata_json}
        )

        receipt = await broker.publish(dlq_record.topic_name, envelope)

        # Update DLQ record state
        dlq_record.status = "REPLAYED"
        dlq_record.retry_count += 1
        dlq_record.replayed_at = datetime.now(timezone.utc)
        session.commit()

        logger.info("Successfully replayed DLQ record id=%s to topic=%s", dlq_id, dlq_record.topic_name)

        return {
            "dlq_id": dlq_id,
            "status": "REPLAYED",
            "topic": dlq_record.topic_name,
            "broker_receipt": receipt,
        }
