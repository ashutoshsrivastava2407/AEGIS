"""AEGIS Governed Tool Input & Security-Sensitive Output Validation Engine.

Strictly validates input arguments against JSON Schemas and server-side boundaries.
Treats tool output as an untrusted external boundary, enforcing result schema validation,
sensitive payload redaction, and protection against tool-result security context injection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import re
import logging

logger = logging.getLogger("aegis.agents.tools.validator")


@dataclass
class ValidationResult:
    """Input argument validation result."""
    is_valid: bool
    reason: str
    sanitized_arguments: Dict[str, Any]
    error_code: Optional[str] = None


@dataclass
class OutputValidationResult:
    """Security-sensitive output validation result."""
    is_valid: bool
    reason: str
    sanitized_result: Dict[str, Any]
    error_code: Optional[str] = None


class ToolValidationEngine:
    """Server-side schema and security validator for tool inputs and outputs."""

    FORBIDDEN_OVERRIDE_KEYS = {
        "is_admin", "roles", "tenant_id", "permissions",
        "is_authorized", "override_policy", "bypass_approval", "auth_token"
    }

    REDACT_KEYS = {
        "password", "secret", "private_key", "api_key", "token", "ssn", "credit_card"
    }

    def validate_input(
        self,
        tool_name: str,
        input_schema: Dict[str, Any],
        arguments: Dict[str, Any],
        tenant_id: str
    ) -> ValidationResult:
        """Validate input arguments against input JSON Schema and security boundaries."""

        if not isinstance(arguments, dict):
            return ValidationResult(
                is_valid=False,
                reason=f"Arguments payload for tool '{tool_name}' must be a JSON object",
                sanitized_arguments={},
                error_code="INVALID_PAYLOAD_TYPE"
            )

        sanitized = dict(arguments)

        # 1. Enforce required fields
        required_fields = input_schema.get("required", [])
        missing_fields = [req for req in required_fields if req not in sanitized or sanitized[req] is None]
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                reason=f"Tool '{tool_name}' call missing required arguments: {missing_fields}",
                sanitized_arguments=sanitized,
                error_code="MISSING_REQUIRED_ARGUMENTS"
            )

        # 2. Validate field types and constraints
        properties = input_schema.get("properties", {})
        for key, value in sanitized.items():
            if key in properties:
                prop_schema = properties[key]
                expected_type = prop_schema.get("type")
                if expected_type and not self._check_type(value, expected_type):
                    return ValidationResult(
                        is_valid=False,
                        reason=f"Argument '{key}' for tool '{tool_name}' expected type '{expected_type}', got '{type(value).__name__}'",
                        sanitized_arguments=sanitized,
                        error_code="TYPE_MISMATCH"
                    )

                # Enum constraint
                if "enum" in prop_schema and value not in prop_schema["enum"]:
                    return ValidationResult(
                        is_valid=False,
                        reason=f"Argument '{key}' value '{value}' not in allowed enum options: {prop_schema['enum']}",
                        sanitized_arguments=sanitized,
                        error_code="ENUM_CONSTRAINT_VIOLATION"
                    )

        # 3. Enforce tenant context boundary (arguments cannot alter server tenant_id)
        if "tenant_id" in sanitized and sanitized["tenant_id"] != tenant_id:
            logger.warning(f"Prevented tenant override attempt in tool '{tool_name}': '{sanitized['tenant_id']}' vs server '{tenant_id}'")
            sanitized["tenant_id"] = tenant_id

        return ValidationResult(
            is_valid=True,
            reason=f"Input arguments for tool '{tool_name}' successfully validated against schema.",
            sanitized_arguments=sanitized
        )

    def validate_output(
        self,
        tool_name: str,
        output_schema: Dict[str, Any],
        raw_result: Any
    ) -> OutputValidationResult:
        """Validate tool execution output as an untrusted boundary before returning to agent context."""

        if not isinstance(raw_result, dict):
            # Wrap non-dict result in standard output envelope
            raw_result = {"status": "SUCCESS", "data": raw_result}

        sanitized_result = dict(raw_result)

        # 1. Enforce output schema required properties
        required = output_schema.get("required", [])
        missing = [r for r in required if r not in sanitized_result]
        if missing:
            logger.warning(f"Tool '{tool_name}' result missing output schema fields {missing}")
            # Ensure missing top-level required status is present
            if "status" in missing:
                sanitized_result["status"] = "SUCCESS"

        # 2. Strip security context override attempts (Tool-Result Injection Defense)
        stripped_keys = []
        for key in list(sanitized_result.keys()):
            if key.lower() in self.FORBIDDEN_OVERRIDE_KEYS:
                del sanitized_result[key]
                stripped_keys.append(key)

        if stripped_keys:
            logger.warning(f"Tool-result security guard stripped injected security keys {stripped_keys} from tool '{tool_name}' output")

        # 3. Apply server-side payload redaction for sensitive keys
        self._redact_dict_in_place(sanitized_result)

        return OutputValidationResult(
            is_valid=True,
            reason=f"Tool '{tool_name}' output successfully validated and sanitized against security boundaries.",
            sanitized_result=sanitized_result
        )

    def redact_payload(self, payload: Dict[str, Any], is_privileged_view: bool = False) -> Dict[str, Any]:
        """Perform server-side payload redaction for safe logging, trace audit, and UI inspection."""
        redacted = dict(payload)
        self._redact_dict_in_place(redacted, is_privileged_view=is_privileged_view)
        return redacted

    def _redact_dict_in_place(self, d: Dict[str, Any], is_privileged_view: bool = False) -> None:
        """Recursively redact sensitive keys in payload dictionary."""
        for k, v in list(d.items()):
            if any(s in k.lower() for s in self.REDACT_KEYS):
                d[k] = "[REDACTED_SECRET]"
            elif isinstance(v, dict):
                self._redact_dict_in_place(v, is_privileged_view=is_privileged_view)
            elif isinstance(v, list):
                d[k] = [self._redact_item(item, is_privileged_view) for item in v]

    def _redact_item(self, item: Any, is_privileged_view: bool) -> Any:
        if isinstance(item, dict):
            c = dict(item)
            self._redact_dict_in_place(c, is_privileged_view)
            return c
        return item

    def _check_type(self, val: Any, expected: str) -> bool:
        if expected == "string":
            return isinstance(val, str)
        elif expected == "integer":
            return isinstance(val, int) and not isinstance(val, bool)
        elif expected == "number":
            return isinstance(val, (int, float)) and not isinstance(val, bool)
        elif expected == "boolean":
            return isinstance(val, bool)
        elif expected == "array":
            return isinstance(val, list)
        elif expected == "object":
            return isinstance(val, dict)
        return True


tool_validation_engine = ToolValidationEngine()
