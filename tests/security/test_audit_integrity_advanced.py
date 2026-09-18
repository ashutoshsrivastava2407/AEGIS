"""Security Unit Tests for Audit Segment Checkpointing, Trust Anchors, and Tampering Detection."""

import pytest
from services.security.audit_integrity import TamperEvidentAuditTrail
from services.security.trust_anchors import LocalVerificationAnchor, ObjectStorageAnchor, ExternalTrustAnchor


def test_audit_segment_checkpointing_and_anchoring():
    trail = TamperEvidentAuditTrail(trust_anchor=LocalVerificationAnchor())
    events = [
        {"id": "ev1", "actor_id": "u1", "action": "LOGIN", "details": {"ip": "1.1.1.1"}},
        {"id": "ev2", "actor_id": "u1", "action": "EXECUTE", "details": {"target": "wf1"}},
    ]
    chain = trail.build_audit_chain(events)
    checkpoint = trail.create_segment_checkpoint(chain)

    assert checkpoint["trust_boundary"] == "LOCAL_TRANSACTIONAL"
    assert checkpoint["anchor_status"] == "ANCHORED"

    ver = trail.verify_chain_integrity(chain, checkpoint)
    assert ver["valid"] is True
    assert ver["checkpoint_valid"] is True


def test_trust_anchor_verification_boundaries():
    # 1. Simulated External Anchor
    sim_anchor = ObjectStorageAnchor()
    trail_sim = TamperEvidentAuditTrail(trust_anchor=sim_anchor)
    chain_sim = trail_sim.build_audit_chain([{"id": "ev1", "actor_id": "u1", "action": "LOGIN"}])
    ckpt_sim = trail_sim.create_segment_checkpoint(chain_sim)
    assert ckpt_sim["trust_boundary"] == "SIMULATED_EXTERNAL_ANCHOR"

    # 2. Independent External Anchor
    ext_anchor = ExternalTrustAnchor()
    trail_ext = TamperEvidentAuditTrail(trust_anchor=ext_anchor)
    chain_ext = trail_ext.build_audit_chain([{"id": "ev1", "actor_id": "u1", "action": "LOGIN"}])
    ckpt_ext = trail_ext.create_segment_checkpoint(chain_ext)
    assert ckpt_ext["trust_boundary"] == "EXTERNALLY_ANCHORED"

    ver_ext = trail_ext.verify_chain_integrity(chain_ext, ckpt_ext)
    assert ver_ext["valid"] is True


def test_audit_chain_truncation_and_reordering_detection():
    trail = TamperEvidentAuditTrail()
    events = [
        {"id": "ev1", "actor_id": "u1", "action": "LOGIN"},
        {"id": "ev2", "actor_id": "u1", "action": "POLICY_EVALUATE"},
        {"id": "ev3", "actor_id": "u1", "action": "WORKFLOW_EXECUTE"},
    ]
    chain = trail.build_audit_chain(events)

    # Reorder events
    reordered_chain = [chain[0], chain[2], chain[1]]
    ver_reorder = trail.verify_chain_integrity(reordered_chain)
    assert ver_reorder["valid"] is False
    assert ver_reorder["tampered_events_count"] > 0
