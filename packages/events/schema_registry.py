"""AEGIS Event Schema Registry.

Provides schema registration, versioning, and validation for streaming event payloads.
"""

import logging
from typing import Any, Dict, Optional
from packages.events.envelope import EventEnvelope

logger = logging.getLogger("aegis.events.schema_registry")


class SchemaValidationError(Exception):
    """Raised when an event payload fails schema validation."""
    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(message)
        self.errors = errors or []


class SchemaRegistry:
    """In-memory and persistent schema registry for streaming events."""

    def __init__(self):
        # Maps (event_type, schema_version) -> Dict[str, FieldSpec]
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def register_schema(
        self,
        event_type: str,
        schema_version: str,
        required_fields: list[str],
        field_types: Optional[Dict[str, str]] = None
    ) -> None:
        """Register a schema specification for an event type and version."""
        key = f"{event_type}:{schema_version}"
        self._schemas[key] = {
            "event_type": event_type,
            "schema_version": schema_version,
            "required_fields": required_fields,
            "field_types": field_types or {},
        }
        logger.info("Registered event schema for key=%s", key)

    def validate(self, envelope: EventEnvelope) -> bool:
        """Validate an event envelope against registered schema.
        
        If no schema is registered for the event type & version, allows the envelope (permissive default)
        unless strict mode is enforced.
        """
        key = f"{envelope.event_type}:{envelope.schema_version}"
        schema = self._schemas.get(key)
        if not schema:
            # Fallback lookup by event_type only
            matching_keys = [k for k in self._schemas if k.startswith(f"{envelope.event_type}:")]
            if matching_keys:
                schema = self._schemas[matching_keys[-1]]

        if not schema:
            # Unregistered schema - basic structural validation
            if not envelope.event_type or not envelope.tenant_id:
                raise SchemaValidationError("Event missing mandatory envelope header fields")
            return True

        # Validate required fields in payload
        payload = envelope.payload or {}
        missing_fields = [field for field in schema["required_fields"] if field not in payload or payload[field] is None]
        if missing_fields:
            raise SchemaValidationError(
                f"Event payload missing required fields: {missing_fields}",
                errors=missing_fields
            )

        # Validate field types if specified
        type_errors = []
        for field, expected_type in schema.get("field_types", {}).items():
            if field in payload and payload[field] is not None:
                val = payload[field]
                if expected_type == "string" and not isinstance(val, str):
                    type_errors.append(f"Field '{field}' expected string, got {type(val).__name__}")
                elif expected_type == "number" and not isinstance(val, (int, float)):
                    type_errors.append(f"Field '{field}' expected number, got {type(val).__name__}")
                elif expected_type == "boolean" and not isinstance(val, bool):
                    type_errors.append(f"Field '{field}' expected boolean, got {type(val).__name__}")
                elif expected_type == "object" and not isinstance(val, dict):
                    type_errors.append(f"Field '{field}' expected object, got {type(val).__name__}")
                elif expected_type == "array" and not isinstance(val, list):
                    type_errors.append(f"Field '{field}' expected array, got {type(val).__name__}")

        if type_errors:
            raise SchemaValidationError(
                f"Event payload type mismatch: {'; '.join(type_errors)}",
                errors=type_errors
            )

        return True


# Global default schema registry instance
global_schema_registry = SchemaRegistry()
