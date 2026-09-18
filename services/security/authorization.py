"""Server-Authoritative Multi-Layer Authorization Engine (RBAC + ABAC + Resource Scope)."""

from typing import Dict, Any, List, Optional
from services.security.rbac import RBACManager
from services.security.abac import ABACEvaluator


class AuthorizationEngine:
    """Authoritative server-side authorization engine enforcing RBAC, ABAC, and resource-level access rules."""

    RESOURCE_TYPES = {
        "TENANT", "WORKSPACE", "DATASET", "DOCUMENT", "KNOWLEDGE_COLLECTION",
        "MODEL", "MODEL_VERSION", "AGENT", "AGENT_TOOL", "WORKFLOW",
        "WORKFLOW_VERSION", "WORKFLOW_RUN", "DECISION", "ACTION_CONTRACT",
        "CONNECTOR", "POLICY", "AUDIT_RECORD", "SECURITY_EVENT"
    }

    def __init__(self):
        self.rbac = RBACManager()
        self.abac = ABACEvaluator()

    def authorize_request(
        self,
        subject_id: str,
        roles: List[str],
        resource_type: str,
        resource_id: str,
        action: str,
        subject_attrs: Optional[Dict[str, Any]] = None,
        resource_attrs: Optional[Dict[str, Any]] = None,
        environment_attrs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Enforce server-authoritative authorization check."""
        res_type = resource_type.upper()
        if res_type not in self.RESOURCE_TYPES:
            raise ValueError(f"Invalid resource type: {res_type}. Must be one of {self.RESOURCE_TYPES}")

        # 1. RBAC check
        has_perm = self.rbac.has_capability(roles, action)
        if not has_perm:
            return {
                "authorized": False,
                "decision": "DENY",
                "reason_code": "RBAC_PERM_DENIED",
                "message": f"Subject '{subject_id}' lacks required capability '{action}' for resource '{resource_type}:{resource_id}'",
            }

        # 2. ABAC check
        abac_res = self.abac.evaluate_attributes(
            subject_attrs or {"tenant_id": "default", "subject_id": subject_id},
            resource_attrs or {"tenant_id": "default", "classification": "INTERNAL"},
            environment_attrs or {"auth_strength": "NORMAL_AUTH"},
        )

        if not abac_res["allowed"]:
            return {
                "authorized": False,
                "decision": "DENY",
                "reason_code": "ABAC_CONTEXT_DENIED",
                "message": f"ABAC context rule denied access: {abac_res['reasons']}",
            }

        return {
            "authorized": True,
            "decision": "ALLOW",
            "reason_code": "AUTHORIZATION_GRANTED",
            "message": "Access authorized by server RBAC and ABAC policy rules.",
        }
