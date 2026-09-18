"""Test suite for Disaster Recovery, Backup Tracking & Restore Verification."""

import pytest
from services.operations.recovery import DisasterRecoveryService


def test_backup_creation_and_listing():
    dr_service = DisasterRecoveryService()
    
    bkp = dr_service.create_backup(
        backup_type="FULL",
        size_bytes=524288000,
        storage_location="s3://aegis-dr/bkp-full-001.tar.gz",
    )
    assert bkp["backup_type"] == "FULL"
    assert bkp["status"] == "COMPLETED"
    assert bkp["checksum"] is not None

    backups = dr_service.list_backups()
    assert len(backups) >= 1
    assert backups[0]["id"] == bkp["id"]


def test_restore_verification_and_rto_calculation():
    dr_service = DisasterRecoveryService()
    
    bkp = dr_service.create_backup(backup_type="INCREMENTAL")
    
    # Authorized DR restore
    restore = dr_service.verify_and_trigger_restore(
        backup_id=bkp["id"],
        target_environment="dr-staging",
        user_role="ENTERPRISE_ADMIN",
    )
    assert restore["status"] == "COMPLETED"
    assert restore["verification_status"] == "VERIFIED_PASSED"
    assert restore["rto_seconds"] > 0.0

    # Unauthorized DR restore blocked by policy
    blocked = dr_service.verify_and_trigger_restore(
        backup_id=bkp["id"],
        target_environment="production",
        user_role="GUEST_USER",
    )
    assert blocked["status"] == "BLOCKED_BY_POLICY"
