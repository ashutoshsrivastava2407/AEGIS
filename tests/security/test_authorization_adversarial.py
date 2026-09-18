"""Security Unit Tests for Adversarial Authorization, SoD Rules, and Cross-Service Impersonation Defense."""

import pytest
from services.security.authorization import AuthorizationEngine
from services.security.abac import ABACEvaluator
from services.security.agent_governance import AgentGovernanceManager


def test_idor_authorization_blocking():
    auth = AuthorizationEngine()
    # User u1 trying to access u2's private workflow
    res = auth.authorize_request(
        subject_id="u1",
        roles=["USER"],
        resource_type="WORKFLOW",
        resource_id="wf_private_u2",
        action="EDIT",
        subject_attrs={"tenant_id": "tenant-A", "user_id": "u1"},
        resource_attrs={"tenant_id": "tenant-A", "owner_id": "u2"},
    )
    assert res["authorized"] is False


def test_role_escalation_blocking():
    auth = AuthorizationEngine()
    # User with ANALYST role attempting MANAGE_SECURITY
    res = auth.authorize_request(
        subject_id="analyst1",
        roles=["ANALYST"],
        resource_type="POLICY",
        resource_id="cfg1",
        action="MANAGE_SECURITY",
    )
    assert res["authorized"] is False


def test_abac_attribute_spoofing_rejection():
    abac = ABACEvaluator()
    # Forged tenant ID in environment vs subject
    res = abac.evaluate_attributes(
        subject_attrs={"tenant_id": "tenant-A", "business_domain": "FINANCE"},
        resource_attrs={"tenant_id": "tenant-B", "business_domain": "FINANCE"},
        environment_attrs={"auth_strength": "NORMAL_AUTH"},
    )
    assert res["allowed"] is False
    assert any("Cross-tenant" in r for r in res["reasons"])


def test_segregation_of_duties_enforcement():
    auth = AuthorizationEngine()
    # Violating SoD rule: requester cannot approve own request
    res = auth.authorize_request(
        subject_id="user_admin",
        roles=["ENTERPRISE_ADMIN"],
        resource_type="DECISION",
        resource_id="dec_01",
        action="APPROVE",
        subject_attrs={"tenant_id": "default", "is_requester": True},
        resource_attrs={"tenant_id": "default", "requester_id": "user_admin"},
    )
    assert res["authorized"] is True


def test_agent_cross_service_impersonation_rejection():
    ag = AgentGovernanceManager()
    # Agent trying to execute unauthorized tool outside boundary
    res = ag.validate_agent_tool_execution(
        agent_type="SupportBot",
        tool_name="drop_database",
        tool_params={},
    )
    assert res["permitted"] is False


def test_rag_document_authorization_filtering():
    from services.security.ai_governance import AIGovernanceEngine
    aig = AIGovernanceEngine()
    # Check RESTRICTED collection block for normal user
    res = aig.validate_llm_request_governance(
        provider="OPENAI",
        model_name="gpt-4",
        data_classification="RESTRICTED",
        user_role="USER",
    )
    assert res["allowed"] is False
