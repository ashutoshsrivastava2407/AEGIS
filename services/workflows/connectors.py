"""Governed Connector Framework with Secret Reference Storage, Redaction, and SSRF Egress Defense."""

import re
import uuid
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from packages.database.models.workflow_execution import WorkflowConnectorModel


class GovernedConnectorManager:
    """Manages integration connectors with zero raw credential leakage, log redaction, and SSRF egress security."""

    SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "auth", "private_key", "credential"}
    DISALLOWED_IP_PATTERNS = [
        re.compile(r"^127\."),
        re.compile(r"^10\."),
        re.compile(r"^172\.(1[6-9]|2[0-9]|3[0-1])\."),
        re.compile(r"^192\.168\."),
        re.compile(r"^169\.254\."),
        re.compile(r"^localhost$", re.IGNORECASE),
        re.compile(r"^0\.0\.0\.0$"),
    ]

    def create_connector(
        self,
        name: str,
        connector_type: str,
        auth_type: str,
        non_secret_config: Dict[str, Any],
        secret_refs: Dict[str, Any],
        egress_allowlist: List[str],
        tenant_id: str = "default",
    ) -> WorkflowConnectorModel:
        """Create a connector record guaranteeing secret_refs separation and no raw credential persistence."""
        # Sanity check: Ensure non_secret_config does not contain raw passwords/secrets
        for key in non_secret_config.keys():
            if any(s in key.lower() for s in self.SENSITIVE_KEYS):
                raise ValueError(f"Raw sensitive key '{key}' found in non_secret_config! Store reference in secret_refs_json.")

        return WorkflowConnectorModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            connector_type=connector_type.upper(),
            auth_type=auth_type.upper(),
            non_secret_config_json=non_secret_config,
            secret_refs_json=secret_refs,
            egress_allowlist_json={"hosts": egress_allowlist},
            is_active=True,
            created_by="system",
            updated_by="system",
        )

    def validate_egress_url(self, target_url: str, allowlist: List[str]) -> bool:
        """Enforce SSRF defenses: block internal loopback/metadata IPs and verify egress allowlist."""
        parsed = urlparse(target_url)
        host = parsed.hostname or parsed.path

        if not host:
            raise ValueError("Invalid target URL for connector egress.")

        # Check SSRF forbidden host patterns
        for pattern in self.DISALLOWED_IP_PATTERNS:
            if pattern.search(host):
                raise SecurityError(f"SSRF Protection: Blocked egress to forbidden internal host '{host}'")

        # Verify host against allowlist if allowlist is populated
        if allowlist and "*" not in allowlist:
            if not any(host == domain or host.endswith("." + domain) for domain in allowlist):
                raise SecurityError(f"Egress Security: Host '{host}' not in connector allowlist {allowlist}")

        return True

    def sanitize_for_logging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive fields from dictionaries before writing to logs, traces, or audit records."""
        sanitized = {}
        for k, v in data.items():
            if any(s in k.lower() for s in self.SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = self.sanitize_for_logging(v)
            else:
                sanitized[k] = v
        return sanitized


class SecurityError(Exception):
    """Raised when SSRF or Egress security rules are violated."""
    pass
