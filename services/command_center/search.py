"""Global Enterprise Search Engine with Strict Authorization Boundaries."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from packages.security import UserContext


class GlobalEnterpriseSearchEngine:
    """Enterprise-wide multi-entity search engine with strict authorization filtering."""

    ENTITY_TYPES = [
        "datasets",
        "kpis",
        "models",
        "documents",
        "knowledge_collections",
        "agents",
        "agent_runs",
        "decisions",
        "simulations",
        "workflows",
        "workflow_runs",
        "incidents",
        "deployments",
        "services",
        "changes",
        "policies",
        "audit_events",
    ]

    def search(
        self,
        query: str,
        user: UserContext,
        target_entities: Optional[List[str]] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Execute authorized global enterprise search across all AEGIS domain entities."""
        q = query.strip().lower()
        entities = target_entities or self.ENTITY_TYPES
        results = []

        # 1. Enforce Authentication & Tenant Boundary
        tenant_id = getattr(user, "tenant_id", "default")
        user_roles = getattr(user, "roles", ["USER"])

        if not q:
            return {
                "query": query,
                "total_results": 0,
                "results": [],
                "entities_searched": entities,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # 2. Search index across domains
        mock_index = [
            {"id": "ds-gold-rev", "type": "datasets", "title": "Revenue Transactions Gold Dataset", "domain": "Data Platform", "tenant_id": "tenant-alpha", "required_role": "USER"},
            {"id": "kpi-mrr", "type": "kpis", "title": "Monthly Recurring Revenue KPI", "domain": "Analytics", "tenant_id": "tenant-alpha", "required_role": "USER"},
            {"id": "mdl-churn", "type": "models", "title": "Customer Churn Prediction Model v2", "domain": "ML Platform", "tenant_id": "tenant-alpha", "required_role": "USER"},
            {"id": "doc-sec-audit", "type": "documents", "title": "SOC 2 Type II Security Compliance Audit", "domain": "Governance", "tenant_id": "tenant-alpha", "required_role": "ENTERPRISE_ADMIN"},
            {"id": "agt-inv-specialist", "type": "agents", "title": "Root Cause Investigation Specialist Agent", "domain": "Agents", "tenant_id": "tenant-alpha", "required_role": "USER"},
            {"id": "dec-infra-001", "type": "decisions", "title": "Automated Infrastructure Scale Out Decision Manifest", "domain": "Decisions", "tenant_id": "tenant-alpha", "required_role": "USER"},
            {"id": "wf-saga-002", "type": "workflows", "title": "High-Availability Failover Saga Workflow", "domain": "Workflows", "tenant_id": "tenant-alpha", "required_role": "USER"},
            {"id": "inc-sev1-lock", "type": "incidents", "title": "SEV1 Database Connection Pool Contention", "domain": "Operations", "tenant_id": "tenant-alpha", "required_role": "USER"},
            {"id": "dep-canary-2.4", "type": "deployments", "title": "Deployment Release v2.4.0 (Canary Rollout)", "domain": "Operations", "tenant_id": "tenant-alpha", "required_role": "USER"},
            {"id": "pol-abac-strict", "type": "policies", "title": "Strict Row Level Security Policy Rule", "domain": "Governance", "tenant_id": "tenant-alpha", "required_role": "ENTERPRISE_ADMIN"},
        ]

        for item in mock_index:
            # Check query string match
            if q in item["title"].lower() or q in item["type"].lower() or q in item["domain"].lower():
                # Enforce Tenant Isolation
                if item["tenant_id"] != tenant_id:
                    continue

                # Enforce RBAC/ABAC Result Filtering (never leak entity existence)
                required_role = item.get("required_role", "USER")
                if required_role == "ENTERPRISE_ADMIN" and "ENTERPRISE_ADMIN" not in user_roles:
                    continue

                results.append({
                    "id": item["id"],
                    "entity_type": item["type"],
                    "title": item["title"],
                    "domain": item["domain"],
                    "relevance_score": 0.95,
                })

        return {
            "query": query,
            "total_results": len(results),
            "results": results[:limit],
            "entities_searched": entities,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
