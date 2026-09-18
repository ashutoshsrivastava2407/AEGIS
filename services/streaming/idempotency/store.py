"""AEGIS Idempotency Store.

Durable & in-memory event deduplication store using (tenant_id, event_id) composite keys.
"""

from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Tuple

logger = logging.getLogger("aegis.streaming.idempotency")


class IdempotencyStore:
    """Event deduplication store managing composite (tenant_id, event_id) keys."""

    def __init__(self, ttl_seconds: int = 86400):
        self.ttl_seconds = ttl_seconds
        # Maps (tenant_id, event_id) -> expiration_datetime
        self._processed: Dict[Tuple[str, str], datetime] = {}

    def is_duplicate(self, tenant_id: str, event_id: str) -> bool:
        """Check if event has already been processed for this tenant."""
        key = (tenant_id, event_id)
        exp = self._processed.get(key)
        if not exp:
            return False
        
        now = datetime.now(timezone.utc)
        if now > exp:
            # Expired entry
            del self._processed[key]
            return False
        
        return True

    def mark_processed(self, tenant_id: str, event_id: str) -> None:
        """Record event as processed with TTL expiry."""
        key = (tenant_id, event_id)
        expiry = datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds)
        self._processed[key] = expiry

    def prune_expired(self) -> int:
        """Prune expired entries from memory store."""
        now = datetime.now(timezone.utc)
        expired_keys = [k for k, exp in self._processed.items() if now > exp]
        for k in expired_keys:
            del self._processed[k]
        return len(expired_keys)

    def count(self) -> int:
        """Total active processed events tracked."""
        return len(self._processed)


# Global singleton instance
global_idempotency_store = IdempotencyStore()
