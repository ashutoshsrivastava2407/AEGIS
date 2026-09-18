"""AEGIS Real-Time Medallion Stream Processor.

Sinks real-time event streams into Bronze raw object storage and Silver conformed object storage.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Dict, Any, List, Optional
from packages.events.envelope import EventEnvelope
from packages.storage.base import ObjectStorage
from packages.storage.filesystem import FilesystemObjectStorage

logger = logging.getLogger("aegis.streaming.medallion")


class MedallionStreamProcessor:
    """Streams real-time event payloads to Bronze and Silver Medallion layers."""

    def __init__(self, storage: Optional[ObjectStorage] = None):
        self.storage = storage or FilesystemObjectStorage()

    async def process_bronze_stream(
        self,
        tenant_id: str,
        topic_name: str,
        events: List[EventEnvelope]
    ) -> Dict[str, Any]:
        """Sink raw streaming event batch to Bronze layer (JSONL)."""
        if not events:
            return {"stored": False, "count": 0}

        now = datetime.now(timezone.utc)
        date_path = now.strftime("%Y/%m/%d/%H")
        key = f"bronze/realtime/{tenant_id}/{topic_name}/{date_path}/raw_events_{int(now.timestamp())}.jsonl"

        lines = [json.dumps(ev.to_dict()) for ev in events]
        content = "\n".join(lines).encode("utf-8")

        result = await self.storage.put_object(key, content, content_type="application/x-ndjson")
        size = result.get("byte_size", result.get("size_bytes", 0))
        logger.info("Persisted Bronze realtime stream key=%s count=%d", key, len(events))
        return {"stored": True, "key": key, "count": len(events), "size_bytes": size}

    async def process_silver_stream(
        self,
        tenant_id: str,
        topic_name: str,
        valid_events: List[EventEnvelope]
    ) -> Dict[str, Any]:
        """Sink schema-validated conformed event batch to Silver layer (JSONL)."""
        if not valid_events:
            return {"stored": False, "count": 0}

        now = datetime.now(timezone.utc)
        key = f"silver/realtime/{tenant_id}/{topic_name}/v1/data_{int(now.timestamp())}.jsonl"

        conformed_records = []
        for ev in valid_events:
            conformed = {
                "event_id": ev.event_id,
                "event_type": ev.event_type,
                "tenant_id": ev.tenant_id,
                "entity_type": ev.entity_type,
                "entity_id": ev.entity_id,
                "occurred_at": ev.occurred_at,
                "schema_version": ev.schema_version,
                **ev.payload
            }
            conformed_records.append(json.dumps(conformed))

        content = "\n".join(conformed_records).encode("utf-8")
        result = await self.storage.put_object(key, content, content_type="application/x-ndjson")
        size = result.get("byte_size", result.get("size_bytes", 0))
        logger.info("Persisted Silver realtime stream key=%s count=%d", key, len(valid_events))
        return {"stored": True, "key": key, "count": len(valid_events), "size_bytes": size}
