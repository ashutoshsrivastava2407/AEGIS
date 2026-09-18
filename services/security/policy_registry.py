"""Declarative Policy Catalog, Immutable Versioning, and State Machine Registry."""

import hashlib
import json
import uuid
from typing import Dict, Any, List, Optional
from packages.database.models.policy import SecurityPolicyModel, SecurityPolicyVersionModel, SecurityPolicyRuleModel


class PolicyRegistry:
    """Manages security policy master definitions, rules, immutable versions, and state machine transitions."""

    VALID_STATES = {"DRAFT", "VALIDATED", "APPROVED", "ACTIVE", "PAUSED", "RETIRED"}
    CATEGORIES = {
        "AUTHENTICATION", "AUTHORIZATION", "DATA_ACCESS", "NETWORK", "CONNECTOR",
        "AI", "AGENT", "WORKFLOW", "ACTION", "MODEL", "RETENTION", "EXPORT",
        "AUDIT", "PRIVILEGED_ACCESS"
    }

    def compute_policy_fingerprint(self, rules_json: Dict[str, Any]) -> str:
        """Compute SHA-256 fingerprint of published policy rules definition."""
        canonical_str = json.dumps(rules_json, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def create_policy(
        self,
        name: str,
        category: str,
        description: str = "",
        owner: str = "security-admin@aegis.enterprise",
        tenant_id: str = "default",
    ) -> SecurityPolicyModel:
        """Create a new security policy in DRAFT status."""
        cat_upper = category.upper()
        if cat_upper not in self.CATEGORIES:
            raise ValueError(f"Invalid policy category: {cat_upper}")

        return SecurityPolicyModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            description=description,
            category=cat_upper,
            status="DRAFT",
            version=1,
            active_version_id=None,
            created_by=owner,
            updated_by=owner,
        )

    def publish_version(
        self,
        policy: SecurityPolicyModel,
        rules_json: Dict[str, Any],
        created_by: str = "system",
    ) -> SecurityPolicyVersionModel:
        """Publish immutable, creation-only policy version and compute SHA-256 fingerprint."""
        fingerprint = self.compute_policy_fingerprint(rules_json)
        version_id = str(uuid.uuid4())
        next_ver = policy.version + 1 if policy.active_version_id else 1

        version_model = SecurityPolicyVersionModel(
            id=version_id,
            tenant_id=policy.tenant_id,
            policy_id=policy.id,
            version_number=next_ver,
            fingerprint=fingerprint,
            rules_json=rules_json,
            is_active=True,
            created_by=created_by,
            updated_by=created_by,
        )

        policy.version = next_ver
        policy.active_version_id = version_id
        policy.status = "ACTIVE"
        policy.updated_by = created_by

        return version_model
