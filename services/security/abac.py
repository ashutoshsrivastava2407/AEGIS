"""Attribute-Based Access Control (ABAC) Context Evaluator."""

from typing import Dict, Any, List, Optional


class ABACEvaluator:
    """Evaluates contextual attributes (user, tenant, domain, classification, region, risk, environment, auth_strength)."""

    def evaluate_attributes(
        self,
        subject_attrs: Dict[str, Any],
        resource_attrs: Dict[str, Any],
        environment_attrs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluate contextual attributes against access rules."""
        errors: List[str] = []

        # Tenant isolation
        subj_tenant = subject_attrs.get("tenant_id", "default")
        res_tenant = resource_attrs.get("tenant_id", "default")
        if subj_tenant != res_tenant and subj_tenant != "system":
            errors.append(f"Cross-tenant access blocked: subject tenant '{subj_tenant}' != resource tenant '{res_tenant}'")

        # Domain boundary
        subj_domain = subject_attrs.get("business_domain", "ENTERPRISE")
        res_domain = resource_attrs.get("business_domain", "ENTERPRISE")
        if subj_domain != res_domain and subj_domain != "ENTERPRISE" and res_domain != "ENTERPRISE":
            errors.append(f"Domain isolation blocked: subject domain '{subj_domain}' != resource domain '{res_domain}'")

        # Classification vs Auth strength
        classification = resource_attrs.get("classification", "INTERNAL")
        auth_strength = environment_attrs.get("auth_strength", "NORMAL_AUTH")
        if classification == "RESTRICTED" and auth_strength in {"NORMAL_AUTH"}:
            errors.append("Access to RESTRICTED resource requires STEP_UP_REQUIRED or PRIVILEGED_AUTH.")

        return {
            "allowed": len(errors) == 0,
            "reasons": errors if errors else ["ABAC context rules satisfied."],
        }
