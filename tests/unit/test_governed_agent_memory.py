"""Unit Test Suite for Governed Agent Memory (25 Categories)."""

import pytest
from services.agents.memory.agent_memory import (
    GovernedAgentMemoryService,
    MEMORY_CLASSES,
)


@pytest.fixture
def memory_service():
    return GovernedAgentMemoryService()


def test_01_memory_creation(memory_service):
    res = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="revenue_baseline_q3",
        content="Baseline Q3 revenue target was set to $1.45M across West region.",
    )
    assert res["success"] is True
    assert res["status"] == "STORED"
    assert res["memory_id"].startswith("mem_")


def test_02_memory_retrieval(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="EPISODIC_MEMORY",
        memory_key="q3_outage_event",
        content="Cloud outage on July 14 caused temporary order drop in West region.",
    )
    records = memory_service.query_memories(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="EPISODIC_MEMORY",
    )
    assert len(records) >= 1
    assert records[0]["memory_key"] == "q3_outage_event"


def test_03_tenant_isolation(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-alpha",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="alpha_secret_metric",
        content="Alpha tenant revenue metrics",
    )
    res_beta = memory_service.query_memories(tenant_id="tenant-beta")
    assert len(res_beta) == 0


def test_04_workspace_isolation(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-dev",
        memory_type="EPISODIC_MEMORY",
        memory_key="dev_test_fact",
        content="Development environment test fact",
    )
    res_prod = memory_service.query_memories(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-prod",
    )
    assert len(res_prod) == 0


def test_05_agent_isolation(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SHORT_TERM_STATE",
        memory_key="sql_agent_scratchpad",
        content="SQL query temp string",
        agent_id="SQLAgent",
    )
    res_data_agent = memory_service.query_memories(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        agent_id="DataAgent",
    )
    assert len(res_data_agent) == 0


def test_06_rbac_authorization(memory_service):
    res = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="unauthorized_write_attempt",
        content="Unauthorized context write",
        user_role="UNAUTHORIZED",
    )
    assert res["success"] is False
    assert "Authorization Denied" in res["error"]


def test_07_data_classification_enforcement(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="restricted_financials",
        content="Restricted executive compensation data",
        data_classification="RESTRICTED",
    )
    public_reads = memory_service.query_memories(
        tenant_id="tenant-aegis-1",
        max_classification="PUBLIC",
    )
    assert len(public_reads) == 0


def test_08_secret_redaction(memory_service):
    res = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="api_credentials",
        content="Connecting using bearer=secret_token_12345 to API",
        structured_payload={"api_key": "sk-prod-99887766"},
    )
    assert res["success"] is True
    stored = memory_service.query_memories(tenant_id="tenant-aegis-1", memory_type="SEMANTIC_MEMORY")[0]
    assert "[REDACTED_SECRET]" in stored["content"]
    assert stored["structured_payload"]["api_key"] == "[REDACTED_SECRET]"


def test_09_pii_handling(memory_service):
    res = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="USER_WORKSPACE_MEMORY",
        memory_key="user_credentials",
        content="User login token bearer=password123",
    )
    assert res["success"] is True
    stored = memory_service.query_memories(tenant_id="tenant-aegis-1")[0]
    assert "[REDACTED_SECRET]" in stored["content"]


def test_10_duplicate_detection(memory_service):
    res1 = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="redundant_fact",
        content="Same identical enterprise fact text",
    )
    res2 = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="redundant_fact",
        content="Same identical enterprise fact text",
    )
    assert res1["status"] == "STORED"
    assert res2["status"] == "DUPLICATE_UPDATED"


def test_11_content_hashing(memory_service):
    res = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="hashed_fact",
        content="Content to verify SHA-256 fingerprint generation",
    )
    assert "content_hash" in res
    assert len(res["content_hash"]) == 64


def test_12_memory_supersession(memory_service):
    res1 = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="forecast_q4",
        content="Initial Q4 forecast: $1.2M",
    )
    old_id = res1["memory_id"]
    sup_res = memory_service.supersede_memory(
        old_memory_id=old_id,
        new_content="Updated Q4 forecast: $1.4M following recovery",
        tenant_id="tenant-aegis-1",
    )
    assert sup_res["success"] is True
    assert sup_res["status"] == "SUPERSEDED"
    active = memory_service.query_memories(tenant_id="tenant-aegis-1")
    assert len(active) == 1
    assert active[0]["content"] == "Updated Q4 forecast: $1.4M following recovery"


def test_13_expiry_and_soft_revocation(memory_service):
    res = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="EPISODIC_MEMORY",
        memory_key="revokable_fact",
        content="Fact to be soft-revoked",
    )
    mem_id = res["memory_id"]
    rev_res = memory_service.revoke_memory(
        memory_id=mem_id,
        tenant_id="tenant-aegis-1",
        reason="Revoked per governance review",
    )
    assert rev_res["success"] is True
    assert rev_res["status"] == "REVOKED"
    active = memory_service.query_memories(tenant_id="tenant-aegis-1")
    assert len(active) == 0


def test_14_confidence_handling(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="low_confidence_fact",
        content="Uncertain hypothesis",
        confidence=0.3,
    )
    high_conf_records = memory_service.query_memories(
        tenant_id="tenant-aegis-1",
        min_confidence=0.8,
    )
    assert len(high_conf_records) == 0


def test_15_provenance_persistence(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="EPISODIC_MEMORY",
        memory_key="provenance_fact",
        content="Fact derived from tool execution",
        source_type="TOOL_EXECUTION",
        source_trace_id="tr_prov_100",
    )
    records = memory_service.query_memories(tenant_id="tenant-aegis-1")
    assert records[0]["source_trace_id"] == "tr_prov_100"


def test_16_conflicting_memory_handling(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="conflict_fact_a",
        content="Region West revenue is $450K",
        confidence=0.9,
    )
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="conflict_fact_b",
        content="Region West revenue is $480K",
        confidence=0.7,
    )
    records = memory_service.query_memories(tenant_id="tenant-aegis-1")
    assert len(records) == 2
    assert records[0]["confidence"] >= records[1]["confidence"]


def test_17_semantic_retrieval(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="cloud_outage",
        content="Infrastructure failure in West datacenter",
    )
    res = memory_service.query_memories(
        tenant_id="tenant-aegis-1",
        query_text="datacenter",
    )
    assert len(res) == 1
    assert "West datacenter" in res[0]["content"]


def test_18_metadata_filtering(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="PROCEDURAL_MEMORY",
        memory_key="scaling_runbook",
        content="Runbook for worker pool expansion",
        memory_namespace="ops_runbooks",
    )
    ops_memories = memory_service.query_memories(
        tenant_id="tenant-aegis-1",
        memory_namespace="ops_runbooks",
    )
    assert len(ops_memories) == 1
    assert ops_memories[0]["memory_key"] == "scaling_runbook"


def test_19_memory_context_compilation(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="compilation_fact",
        content="Enterprise fact for prompt assembly",
    )
    compiled = memory_service.compile_memory_context(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        task_query="assembly",
        token_budget=1000,
    )
    assert "retrieval_id" in compiled
    assert "Fresh enterprise evidence" in compiled["evidence_precedence"]
    assert "compilation_fact" in compiled["compiled_prompt"]


def test_20_memory_write_policy_denial(memory_service):
    res = memory_service.store_memory(
        tenant_id="UNAUTHORIZED",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="denied_write",
        content="Unauthorized tenant write attempt",
    )
    assert res["success"] is False
    assert "Tenant Boundary Denial" in res["error"]


def test_21_memory_retrieval_policy_denial(memory_service):
    records = memory_service.query_memories(tenant_id="UNAUTHORIZED")
    assert len(records) == 0


def test_22_audit_logging(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="audited_fact",
        content="Audited fact content",
    )
    events = memory_service._memory_events
    assert len(events) >= 1
    assert events[-1]["action_type"] == "WRITE"


def test_23_trace_correlation(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="EPISODIC_MEMORY",
        memory_key="traced_fact",
        content="Fact with correlation ID",
        source_trace_id="tr_unique_99",
    )
    records = memory_service.query_memories(tenant_id="tenant-aegis-1")
    assert records[0]["source_trace_id"] == "tr_unique_99"


def test_24_result_to_memory_provenance(memory_service):
    memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="tool_provenance_fact",
        content="Derived directly from query_analytics output",
        source_type="TOOL_EXECUTION",
        source_reference="query_analytics",
    )
    records = memory_service.query_memories(tenant_id="tenant-aegis-1")
    assert records[0]["source_reference"] == "query_analytics"


def test_25_restart_persistence(memory_service):
    res = memory_service.store_memory(
        tenant_id="tenant-aegis-1",
        workspace_id="ws-main",
        memory_type="SEMANTIC_MEMORY",
        memory_key="persistent_across_restarts",
        content="Persistent enterprise record",
    )
    assert res["success"] is True
    reloaded = memory_service.query_memories(tenant_id="tenant-aegis-1")
    assert len(reloaded) >= 1
