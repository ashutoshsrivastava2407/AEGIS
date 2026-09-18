"""Security Unit Tests for Break-Glass Emergency Session Activation, Scope Restrictions, and Post-Use Review Lifecycle."""

import pytest
from services.security.privileged_access import BreakGlassManager


def test_break_glass_activation_and_scope_restriction():
    bgm = BreakGlassManager()
    session = bgm.activate_break_glass(
        actor_id="admin_on_call",
        justification="Production Outage Resolution #INC-9912",
        scope_restricted="SERVICE_WORKER_RESTART",
        duration_minutes=30,
    )
    assert session.status == "ACTIVE"
    assert session.scope_restricted == "SERVICE_WORKER_RESTART"
    assert bgm.validate_session(session) is True


def test_break_glass_post_use_review_lifecycle():
    bgm = BreakGlassManager()
    session = bgm.activate_break_glass(
        actor_id="admin_on_call",
        justification="Production Incident Outage",
    )

    review_init = bgm.get_review_record(session.id)
    assert review_init is not None
    assert review_init["review_status"] == "PENDING_REVIEW"

    # Auditor completes post-use review
    reviewed = bgm.submit_post_use_review(
        session_id=session.id,
        reviewer_id="lead_security_auditor",
        status="CLOSED",
        review_notes="Justification verified against incident log #INC-9912. Session closed.",
    )
    assert reviewed["review_status"] == "CLOSED"
    assert reviewed["reviewer_id"] == "lead_security_auditor"
