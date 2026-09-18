"""Role-Based Access Control (RBAC) Manager."""

from typing import Dict, Any, List, Set


class RBACManager:
    """Manages role hierarchies, capability permissions, and subject-role bindings."""

    SYSTEM_ROLES = {
        "ENTERPRISE_ADMIN": {
            "capabilities": {"VIEW", "CREATE", "EDIT", "DELETE", "EXECUTE", "APPROVE", "ADMINISTER", "AUDIT", "EXPORT", "MANAGE_SECURITY", "MANAGE_POLICY", "MANAGE_IDENTITY"},
        },
        "POLICY_ADMIN": {
            "capabilities": {"VIEW", "CREATE", "EDIT", "APPROVE", "AUDIT", "MANAGE_POLICY"},
        },
        "SECURITY_AUDITOR": {
            "capabilities": {"VIEW", "AUDIT", "EXPORT"},
        },
        "WORKFLOW_OPERATOR": {
            "capabilities": {"VIEW", "EXECUTE", "APPROVE"},
        },
        "DATA_STEWARD": {
            "capabilities": {"VIEW", "EDIT", "AUDIT"},
        },
        "SERVICE_ROLE": {
            "capabilities": {"VIEW", "EXECUTE"},
        },
    }

    def has_capability(self, roles: List[str], required_capability: str) -> bool:
        """Check if any assigned role contains the required capability permission."""
        req = required_capability.upper()
        for role in roles:
            rdef = self.SYSTEM_ROLES.get(role.upper(), {})
            if req in rdef.get("capabilities", set()):
                return True
        return False
