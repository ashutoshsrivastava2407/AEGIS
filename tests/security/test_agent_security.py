"""AEGIS Agent Security & Cross-Tenant Policy Test Suite."""

import pytest
from services.agents.tools.authorization import authorization_engine


def test_cross_tenant_tool_authorization_isolation():
    """Verify tool parameter context forces caller tenant ID."""
    res = authorization_engine.authorize_tool_call(
        tool_name="dataset_search",
        params={"query": "financials", "tenant_id": "malicious_tenant"},
        agent_type="DATA",
        tenant_id="authenticated_tenant"
    )
    assert res.is_authorized is True
    # Verify parameter is sanitized to caller's authenticated tenant
    assert res.sanitized_params["tenant_id"] == "authenticated_tenant"


def test_sql_injection_defense_server_side():
    """Verify server-side authorization blocks SQL injection strings."""
    malicious_sqls = [
        "SELECT * FROM sales; DROP TABLE sales;--",
        "DELETE FROM users WHERE 1=1",
        "TRUNCATE TABLE audit_logs",
        "EXEC sp_executesql N'SELECT 1'",
    ]

    for sql in malicious_sqls:
        res = authorization_engine.authorize_tool_call(
            tool_name="analytical_query",
            params={"sql": sql},
            agent_type="SQL",
            tenant_id="tenant-sec"
        )
        assert res.is_authorized is False
        assert "illegal DDL/DML keyword" in res.reason


def test_unauthorized_agent_type_bypass_rejection():
    """Verify agents cannot invoke tools outside their server-side allowlist."""
    # Data agent trying to start a workflow
    res = authorization_engine.authorize_tool_call(
        tool_name="workflow_start",
        params={"workflow_name": "rollback"},
        agent_type="DATA",
        tenant_id="tenant-sec"
    )
    assert res.is_authorized is False
    assert "not granted permission" in res.reason
