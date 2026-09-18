"""AEGIS Canonical Event Envelope.

Defines the standard envelope structure for all real-time streaming events across AEGIS.
"""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class EventEnvelope(BaseModel):
    """Canonical event envelope for real-time event streaming."""
    
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event identifier")
    event_type: str = Field(..., description="Qualified event type (e.g., domain.entity.action)")
    event_version: str = Field(default="1.0.0", description="Semantic version of event type")
    tenant_id: str = Field(..., description="Tenant context isolation identifier")
    source: str = Field(..., description="Source system or component producing the event")
    entity_type: str = Field(..., description="Domain entity class name")
    entity_id: str = Field(..., description="Unique entity identifier")
    occurred_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp when event occurred at source (ISO 8601)"
    )
    produced_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp when event envelope was published to broker (ISO 8601)"
    )
    correlation_id: Optional[str] = Field(default=None, description="Distributed tracing correlation ID")
    schema_version: str = Field(default="1.0", description="Schema specification version")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload dictionary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Operational headers and metadata")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize envelope to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventEnvelope":
        """Parse dictionary into EventEnvelope instance."""
        return cls.model_validate(data)
