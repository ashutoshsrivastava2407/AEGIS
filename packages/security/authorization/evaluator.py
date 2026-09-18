"""RBAC & ABAC Security Evaluator."""

from typing import List
from packages.security.common.models import UserContext


class AuthorizationEvaluator:
    """Evaluates user permissions and resource access policies."""

    def evaluate_permission(self, user: UserContext, required_permission: str) -> bool:
        if user.is_admin:
            return True
        return required_permission in user.permissions

    def evaluate_role(self, user: UserContext, required_role: str) -> bool:
        if user.is_admin:
            return True
        return required_role in user.roles

    def evaluate_tenant_boundary(self, user: UserContext, resource_tenant_id: str) -> bool:
        return user.tenant_id == resource_tenant_id


security_evaluator = AuthorizationEvaluator()
