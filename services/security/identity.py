"""User Account Lifecycle and Non-Human Service Identity Management."""

import uuid
from typing import Dict, Any, List, Optional
from packages.database.models.identity import ServiceIdentityModel
from packages.database.models.user import UserModel


class IdentityManager:
    """Manages user account lifecycle states and profile attributes."""

    VALID_STATUSES = {"ACTIVE", "SUSPENDED", "LOCKED", "DISABLED", "INVITED", "DEPROVISIONED"}

    def transition_user_status(self, user: UserModel, target_status: str) -> UserModel:
        """Transition user status according to valid lifecycle machine."""
        status = target_status.upper()
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid user status: {status}. Must be one of {self.VALID_STATUSES}")
        user.is_active = (status == "ACTIVE")
        return user


class ServiceIdentityManager:
    """Manages non-human identities for workflows, agents, services, connectors, and scheduled jobs."""

    VALID_TYPES = {"WORKFLOW", "AGENT", "SERVICE", "CONNECTOR", "SCHEDULED_JOB"}

    def create_service_identity(
        self,
        name: str,
        identity_type: str,
        description: str = "",
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        allowed_domains: Optional[List[str]] = None,
        risk_ceiling: str = "HIGH_RISK",
        tenant_id: str = "default",
    ) -> ServiceIdentityModel:
        """Create a dedicated non-human service identity with separate policy scope."""
        itype = identity_type.upper()
        if itype not in self.VALID_TYPES:
            raise ValueError(f"Invalid service identity type: {itype}")

        return ServiceIdentityModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            name=name,
            identity_type=itype,
            description=description,
            roles_json={"roles": roles or ["SERVICE_ROLE"]},
            permissions_json={"permissions": permissions or ["READ", "EXECUTE"]},
            allowed_domains_json={"domains": allowed_domains or ["GLOBAL"]},
            risk_ceiling=risk_ceiling.upper(),
            is_active=True,
            created_by="system",
            updated_by="system",
        )
