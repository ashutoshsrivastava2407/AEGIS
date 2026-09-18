"""Ingestion Idempotency Manager."""

import hashlib
import json
from typing import Dict, Any, List


class IdempotencyManager:
    """Computes stable payload checksums to prevent duplicate record processing."""

    def compute_checksum(self, records: List[Dict[str, Any]]) -> str:
        serialized = json.dumps(records, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


idempotency_manager = IdempotencyManager()
