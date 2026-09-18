"""Unit Test Suite for AEGIS Governance, Security, and Compliance Platform Services."""

import pytest
import uuid
from services.security.identity import IdentityManager, ServiceIdentityManager
from services.security.authentication import AuthenticationService
from services.security.sessions import SessionManager
from services.security.mfa import MFAPolicyManager
from services.security.rbac import RBACManager
from services.security.abac import ABACEvaluator
from services.security.authorization import AuthorizationEngine
from services.security.policy_registry import PolicyRegistry
from services.security.policy_engine import ServerPolicyEngine
from services.security.policy_simulator import PolicySimulator
from services.security.exceptions import PolicyExceptionManager
from services.security.privileged_access import PrivilegedAccessManager, BreakGlassManager
from services.security.access_reviews import AccessReviewManager
from services.security.data_governance import DataGovernanceEngine
from services.security.ai_governance import AIGovernanceEngine
from services.security.agent_governance import AgentGovernanceManager
from services.security.workflow_governance import WorkflowGovernanceBridge
from services.security.security_events import SecurityEventLogger
from services.security.security_findings import SecurityFindingManager
from services.security.compliance import ComplianceEngine
from services.security.evidence import ComplianceEvidenceCollector
from services.security.audit_integrity import TamperEvidentAuditTrail
from services.security.threat_detection import SecurityThreatDetector


def test_service_identity_creation():
    mgr = ServiceIdentityManager()
    si = mgr.create_service_identity(
        name="Workflow Executor",
        identity_type="WORKFLOW",
        risk_ceiling="HIGH_RISK",
    )
    assert si.identity_type == "WORKFLOW"
    assert si.is_active is True


def test_authentication_service():
    auth = AuthenticationService()
    res = auth.authenticate_credentials("LOCAL", "user1", "Password123!")
    assert res["authenticated"] is True
    assert res["provider"] == "LOCAL"


def test_session_manager():
    sm = SessionManager()
    session = sm.create_session("user1", auth_provider="LOCAL")
    assert sm.validate_session(session) is True

    sm.revoke_session(session)
    assert sm.validate_session(session) is False


def test_mfa_policy_manager():
    mfa = MFAPolicyManager()
    str1 = mfa.evaluate_required_auth_strength("READ_DATA", "LOW", "INTERNAL")
    assert str1 == "NORMAL_AUTH"

    str2 = mfa.evaluate_required_auth_strength("CHANGE_GOVERNANCE_POLICY", "HIGH", "RESTRICTED")
    assert str2 == "PRIVILEGED_AUTH"


def test_server_authoritative_authorization_engine():
    engine = AuthorizationEngine()
    # Allowed request
    res = engine.authorize_request(
        subject_id="u1",
        roles=["ENTERPRISE_ADMIN"],
        resource_type="WORKFLOW",
        resource_id="wf1",
        action="EXECUTE",
    )
    assert res["authorized"] is True

    # Denied request for invalid role
    res_deny = engine.authorize_request(
        subject_id="u2",
        roles=["SERVICE_ROLE"],
        resource_type="WORKFLOW",
        resource_id="wf1",
        action="MANAGE_SECURITY",
    )
    assert res_deny["authorized"] is False


def test_policy_engine_and_simulator():
    engine = ServerPolicyEngine()
    pol = engine.evaluate_policy("u1", "res1", "EXECUTE", {"risk_level": "LOW"})
    assert pol["decision"] == "ALLOW"

    simulator = PolicySimulator()
    sim = simulator.simulate_policy_impact([], [{"subject_id": "u1", "action": "EXECUTE"}])
    assert sim["total_events_evaluated"] == 1
    assert sim["state_modified"] is False


def test_policy_exception_manager():
    em = PolicyExceptionManager()
    exc = em.request_exception("pol1", "u1", "scope1", "Emergency testing", duration_days=7)
    assert exc.status == "REQUESTED"

    em.approve_exception(exc, "approver1")
    assert em.validate_exception_active(exc) is True


def test_break_glass_manager():
    bgm = BreakGlassManager()
    session = bgm.activate_break_glass("admin1", "Production Incident Response")
    assert bgm.validate_session(session) is True


def test_data_governance_masking():
    dge = DataGovernanceEngine()
    data = {"ssn": "123-45-6789", "email": "admin@aegis.com", "public_field": "hello"}
    masked = dge.mask_sensitive_payload(data, user_role="USER")
    assert masked["ssn"] == "***MASKED***"
    assert masked["public_field"] == "hello"


def test_ai_and_agent_governance():
    aig = AIGovernanceEngine()
    llm_check = aig.validate_llm_request_governance("OPENAI", "gpt-4", "INTERNAL", "USER")
    assert llm_check["allowed"] is True

    # Block RESTRICTED data on external provider
    llm_block = aig.validate_llm_request_governance("OPENAI", "gpt-4", "RESTRICTED", "USER")
    assert llm_block["allowed"] is False

    ag = AgentGovernanceManager()
    agent_check = ag.validate_agent_tool_execution("AutonomousAgent", "scale_service_workers", {})
    assert agent_check["permitted"] is True


def test_tamper_evident_audit_hash_chain():
    trail = TamperEvidentAuditTrail()
    events = [
        {"id": "ev1", "actor_id": "u1", "action": "LOGIN", "details": {"ip": "1.1.1.1"}},
        {"id": "ev2", "actor_id": "u1", "action": "EXECUTE", "details": {"target": "wf1"}},
    ]
    chain = trail.build_audit_chain(events)
    assert len(chain) == 2
    assert chain[0]["previous_hash"] == trail.GENESIS_HASH

    verification = trail.verify_chain_integrity(chain)
    assert verification["valid"] is True


def test_security_threat_detector():
    detector = SecurityThreatDetector()
    event_logger = SecurityEventLogger()

    events = [
        event_logger.log_event("AUTH_FAILURE", "bad_actor"),
        event_logger.log_event("AUTH_FAILURE", "bad_actor"),
        event_logger.log_event("AUTH_FAILURE", "bad_actor"),
    ]

    findings = detector.analyze_event_stream(events)
    assert len(findings) == 1
    assert findings[0].finding_type == "AUTH_FAILURE_BURST"
