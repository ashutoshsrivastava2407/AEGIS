"""Security Unit Tests for Data Governance, Nested PII Masking, Legal Hold, and Data Residency."""

import pytest
from services.security.data_governance import DataGovernanceEngine


def test_nested_and_array_pii_masking():
    dge = DataGovernanceEngine()
    payload = {
        "user_id": "u1",
        "ssn": "999-88-7777",
        "profile": {
            "credit_card": "4111111111111111",
            "bio": "Email user@aegis.com text",
        },
        "logs": [
            "User SSN 123-45-6789 event",
            {"secret": "my_secret_token", "ip": "10.0.0.1"},
        ],
    }
    masked = dge.mask_sensitive_payload(payload, user_role="ANALYST")
    assert masked["ssn"] == "***MASKED***"
    assert masked["profile"]["credit_card"] == "***MASKED***"
    assert "[REDACTED_PII]" in masked["profile"]["bio"]
    assert "[REDACTED_PII]" in masked["logs"][0]
    assert masked["logs"][1]["secret"] == "***MASKED***"


def test_data_export_permission_gating():
    dge = DataGovernanceEngine()
    assert dge.validate_export_permission("CONFIDENTIAL", "ANALYST") is True
    assert dge.validate_export_permission("RESTRICTED", "ANALYST") is False
    assert dge.validate_export_permission("RESTRICTED", "ENTERPRISE_ADMIN") is True


def test_data_residency_enforcement_gating():
    dge = DataGovernanceEngine()
    res_us = dge.validate_data_residency("US", "US")
    assert res_us["allowed"] is True

    res_cross = dge.validate_data_residency("IN", "US")
    assert res_cross["allowed"] is False
    assert res_cross["reason"] == "DATA_RESIDENCY_VIOLATION"


def test_legal_hold_overrides_retention_deletion():
    dge = DataGovernanceEngine()

    # Apply Legal Hold on dataset
    dge.apply_legal_hold(
        resource_type="DATASET",
        resource_id="ds_financial_01",
        case_reference="SEC-2026-CASE-01",
        matter_name="Financial Audit 2026",
        custodian="compliance_officer",
        reason="Litigation Hold for SEC investigation",
    )

    # Evaluate retention cleanup eligibility after 400 days (retention = 365 days)
    check = dge.evaluate_retention_action_eligibility(
        resource_type="DATASET",
        resource_id="ds_financial_01",
        retention_days=365,
        creation_days_ago=400,
    )
    assert check["eligible_for_deletion"] is False
    assert check["reason"] == "BLOCKED_BY_ACTIVE_LEGAL_HOLD"

    # Release Legal Hold
    released = dge.release_legal_hold("DATASET", "ds_financial_01")
    assert released is True

    # Re-evaluate eligibility
    check_after = dge.evaluate_retention_action_eligibility(
        resource_type="DATASET",
        resource_id="ds_financial_01",
        retention_days=365,
        creation_days_ago=400,
    )
    assert check_after["eligible_for_deletion"] is True
    assert check_after["reason"] == "RETENTION_EXPIRED"
