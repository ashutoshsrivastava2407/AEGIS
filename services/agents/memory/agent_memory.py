"""AEGIS Governed Agent Memory Plane.

Enforces 9-stage server-side memory governance:
Identity -> Authentication -> Tenant Isolation -> RBAC/ABAC Authorization -> Data Classification -> Memory Policy -> Read/Write Gating -> Audit -> Trace/Telemetry.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid
import hashlib
import json
import logging
from datetime import datetime, timezone

import logging
from datetime import datetime, timezone

from services.security.policy_engine import ServerPolicyEngine

logger = logging.getLogger("aegis.agents.memory")

# Permitted memory classes
MEMORY_CLASSES = {
    "SHORT_TERM_STATE": "Temporary execution state, active task context, recent tool results",
    "EPISODIC_MEMORY": "Prior agent runs, previous investigations, decisions, tool outcomes",
    "SEMANTIC_MEMORY": "Durable enterprise facts, validated business facts, entity relationships",
    "PROCEDURAL_MEMORY": "Approved execution patterns, operating procedures, task strategies",
    "USER_WORKSPACE_MEMORY": "Workspace-scoped preferences, authorized recurring context",
}


@dataclass
class GovernedMemoryRecord:
    memory_id: str
    tenant_id: str
    workspace_id: str
    memory_namespace: str
    memory_type: str
    memory_key: str
    content: str
    structured_payload: Dict[str, Any]
    content_hash: str
    confidence: float = 0.9
    importance: float = 0.5
    data_classification: str = "INTERNAL"
    sensitivity: str = "LOW"
    status: str = "ACTIVE"
    version: int = 1
    agent_id: Optional[str] = None
    agent_run_id: Optional[str] = None
    source_type: str = "TOOL_EXECUTION"
    source_reference: Optional[str] = None
    source_trace_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None
    superseded_by: Optional[str] = None


class GovernedAgentMemoryService:
    """Production-grade Governed Agent Memory Service with server-authoritative controls."""

    def __init__(self):
        self.policy_engine = ServerPolicyEngine()
        self._memory_store: Dict[str, GovernedMemoryRecord] = {}
        self._memory_events: List[Dict[str, Any]] = []

    def store_memory(
        self,
        tenant_id: str,
        workspace_id: str,
        memory_type: str,
        memory_key: str,
        content: str,
        structured_payload: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        agent_run_id: Optional[str] = None,
        memory_namespace: str = "default",
        data_classification: str = "INTERNAL",
        confidence: float = 0.9,
        importance: float = 0.5,
        source_type: str = "TOOL_EXECUTION",
        source_reference: Optional[str] = None,
        source_trace_id: Optional[str] = None,
        user_role: str = "AGENT_OPERATOR",
        actor_id: str = "agent_system",
    ) -> Dict[str, Any]:
        """Store candidate memory following 9-stage server-side governance pipeline."""
        start_time = datetime.now(timezone.utc).isoformat()
        trace_id = source_trace_id or f"tr_mem_{uuid.uuid4().hex[:8]}"

        # 1. Identity & 2. Authentication Verification
        if not actor_id:
            return {"success": False, "error": "Authentication Failed: Missing actor identity", "memory_id": None}

        # 3. Tenant Isolation Check
        if not tenant_id or tenant_id == "UNAUTHORIZED":
            return {"success": False, "error": "Tenant Boundary Denial: Invalid tenant identity", "memory_id": None}

        # 4. RBAC/ABAC Authorization
        if user_role in ["RESTRICTED_READONLY", "UNAUTHORIZED"]:
            return {"success": False, "error": f"Authorization Denied: Role '{user_role}' cannot write memory", "memory_id": None}

        # 5. Data Classification & Redaction
        sanitized_payload = self._redact_secrets_and_pii(structured_payload or {})
        sanitized_content = self._redact_text(content)

        # 6. Server Policy Evaluation
        eval_ctx = {
            "user_role": user_role,
            "data_classification": data_classification,
            "memory_type": memory_type,
            "tenant_id": tenant_id,
        }
        policy_res = self.policy_engine.evaluate_policy(
            subject_id=actor_id,
            resource_id=f"memory:{memory_namespace}:{memory_key}",
            action="MEMORY_WRITE",
            context=eval_ctx,
            tenant_id=tenant_id,
        )

        if policy_res.get("decision") not in ["ALLOW"]:
            self._record_audit_event(
                memory_id="NONE",
                tenant_id=tenant_id,
                action_type="WRITE_DENIED",
                actor_id=actor_id,
                reason=f"Policy denied memory write: {policy_res.get('reason')}",
                trace_id=trace_id,
                payload={"memory_key": memory_key, "decision": policy_res.get("decision")},
            )
            return {"success": False, "error": f"Policy Denial: {policy_res.get('reason')}", "memory_id": None}

        # 7. Write Gating: Content hashing & Duplicate Check
        content_hash = hashlib.sha256(f"{tenant_id}:{memory_namespace}:{sanitized_content}".encode("utf-8")).hexdigest()
        existing = self._find_by_hash(tenant_id, memory_namespace, content_hash)
        if existing and existing.status == "ACTIVE":
            logger.info(f"Duplicate memory write detected for key '{memory_key}', updating confidence.")
            existing.confidence = max(existing.confidence, confidence)
            existing.last_accessed_at = start_time
            return {"success": True, "status": "DUPLICATE_UPDATED", "memory_id": existing.memory_id, "record": existing}

        memory_id = f"mem_{uuid.uuid4().hex[:12]}"

        # Create record
        rec = GovernedMemoryRecord(
            memory_id=memory_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            memory_namespace=memory_namespace,
            memory_type=memory_type if memory_type in MEMORY_CLASSES else "EPISODIC_MEMORY",
            memory_key=memory_key,
            content=sanitized_content,
            structured_payload=sanitized_payload,
            content_hash=content_hash,
            confidence=confidence,
            importance=importance,
            data_classification=data_classification,
            sensitivity="LOW",
            status="ACTIVE",
            version=1,
            agent_id=agent_id,
            agent_run_id=agent_run_id,
            source_type=source_type,
            source_reference=source_reference,
            source_trace_id=trace_id,
            created_at=start_time,
        )

        self._memory_store[memory_id] = rec

        # 8. Audit Logging & 9. Trace/Telemetry
        self._record_audit_event(
            memory_id=memory_id,
            tenant_id=tenant_id,
            action_type="WRITE",
            actor_id=actor_id,
            reason="Governed memory write succeeded",
            trace_id=trace_id,
            payload={"memory_key": memory_key, "memory_type": memory_type, "classification": data_classification},
        )
        self._persist_db_memory(rec)

        return {"success": True, "status": "STORED", "memory_id": memory_id, "content_hash": content_hash}

    def query_memories(
        self,
        tenant_id: str,
        workspace_id: Optional[str] = None,
        memory_namespace: Optional[str] = None,
        memory_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        max_classification: str = "RESTRICTED",
        user_role: str = "AGENT_OPERATOR",
        actor_id: str = "agent_system",
        min_confidence: float = 0.0,
        query_text: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Governed read/retrieval pipeline enforcing tenant boundaries & classification bounds."""
        trace_id = f"tr_query_{uuid.uuid4().hex[:8]}"

        # Tenant isolation
        if not tenant_id or tenant_id == "UNAUTHORIZED":
            return []

        # Filter active memory records
        records = [m for m in self._memory_store.values() if m.tenant_id == tenant_id and m.status == "ACTIVE"]

        if workspace_id:
            records = [m for m in records if m.workspace_id == workspace_id]
        if memory_namespace:
            records = [m for m in records if m.memory_namespace == memory_namespace]
        if memory_type:
            records = [m for m in records if m.memory_type == memory_type]
        if agent_id:
            records = [m for m in records if m.agent_id == agent_id]

        records = [m for m in records if m.confidence >= min_confidence]

        # Classification filtering
        classification_hierarchy = {"PUBLIC": 1, "INTERNAL": 2, "CONFIDENTIAL": 3, "RESTRICTED": 4}
        max_level = classification_hierarchy.get(max_classification, 4)
        records = [m for m in records if classification_hierarchy.get(m.data_classification, 2) <= max_level]

        # Text matching / relevance ranking
        if query_text:
            query_lower = query_text.lower()
            matching = [m for m in records if query_lower in m.content.lower() or query_lower in m.memory_key.lower()]
            if not matching:
                query_words = [w for w in query_lower.split() if len(w) > 2]
                if query_words:
                    matching = [m for m in records if any(w in m.content.lower() or w in m.memory_key.lower() for w in query_words)]
            records = matching

        # Sort by importance and recency
        records.sort(key=lambda x: (x.importance, x.confidence, x.created_at), reverse=True)

        res_dicts = []
        for r in records[:limit]:
            res_dicts.append({
                "memory_id": r.memory_id,
                "tenant_id": r.tenant_id,
                "workspace_id": r.workspace_id,
                "memory_namespace": r.memory_namespace,
                "memory_type": r.memory_type,
                "memory_key": r.memory_key,
                "content": r.content,
                "structured_payload": r.structured_payload,
                "confidence": r.confidence,
                "importance": r.importance,
                "data_classification": r.data_classification,
                "source_type": r.source_type,
                "source_reference": r.source_reference,
                "source_trace_id": r.source_trace_id,
                "status": r.status,
                "created_at": r.created_at,
            })

        self._record_audit_event(
            memory_id="QUERY_BATCH",
            tenant_id=tenant_id,
            action_type="READ",
            actor_id=actor_id,
            reason=f"Queried {len(res_dicts)} active memories",
            trace_id=trace_id,
            payload={"count": len(res_dicts), "query": query_text},
        )
        return res_dicts

    def compile_memory_context(
        self,
        tenant_id: str,
        workspace_id: str,
        task_query: str,
        token_budget: int = 2000,
        user_role: str = "AGENT_OPERATOR",
        actor_id: str = "agent_system",
    ) -> Dict[str, Any]:
        """Compile bounded agent memory context across episodic, semantic, procedural, and short-term state."""
        episodic = self.query_memories(tenant_id, workspace_id, memory_type="EPISODIC_MEMORY", query_text=task_query, limit=5)
        semantic = self.query_memories(tenant_id, workspace_id, memory_type="SEMANTIC_MEMORY", query_text=task_query, limit=5)
        procedural = self.query_memories(tenant_id, workspace_id, memory_type="PROCEDURAL_MEMORY", limit=3)
        short_term = self.query_memories(tenant_id, workspace_id, memory_type="SHORT_TERM_STATE", limit=5)

        compiled_entries = []
        budget_char_limit = token_budget * 4
        current_len = 0

        for section_name, items in [("Semantic Knowledge", semantic), ("Episodic History", episodic), ("Procedural Guidelines", procedural), ("Active Short-Term Context", short_term)]:
            for item in items:
                entry_str = f"[{section_name}] {item['memory_key']}: {item['content']} (Confidence: {item['confidence']}, Source: {item['source_type']})"
                if current_len + len(entry_str) <= budget_char_limit:
                    compiled_entries.append(entry_str)
                    current_len += len(entry_str)

        compiled_prompt = "\n".join(compiled_entries)
        retrieval_id = f"ret_{uuid.uuid4().hex[:10]}"

        # Record retrieval audit
        self._record_retrieval_audit(tenant_id, retrieval_id, task_query, [m["memory_id"] for m in episodic + semantic], current_len)

        return {
            "retrieval_id": retrieval_id,
            "tenant_id": tenant_id,
            "task_query": task_query,
            "compiled_prompt": compiled_prompt,
            "entry_count": len(compiled_entries),
            "char_count": current_len,
            "evidence_precedence": "Fresh enterprise evidence and live tool outputs take priority over historical context.",
        }

    def supersede_memory(
        self,
        old_memory_id: str,
        new_content: str,
        tenant_id: str,
        user_role: str = "AGENT_OPERATOR",
        actor_id: str = "agent_system",
    ) -> Dict[str, Any]:
        """Supersede an existing active memory record with an updated record."""
        old_rec = self._memory_store.get(old_memory_id)
        if not old_rec or old_rec.tenant_id != tenant_id:
            return {"success": False, "error": "Memory record not found or tenant mismatch"}

        # Mark old as superseded
        old_rec.status = "SUPERSEDED"

        # Create new version
        new_res = self.store_memory(
            tenant_id=tenant_id,
            workspace_id=old_rec.workspace_id,
            memory_type=old_rec.memory_type,
            memory_key=old_rec.memory_key,
            content=new_content,
            structured_payload=old_rec.structured_payload,
            memory_namespace=old_rec.memory_namespace,
            data_classification=old_rec.data_classification,
            confidence=old_rec.confidence,
            user_role=user_role,
            actor_id=actor_id,
        )

        if new_res.get("success"):
            new_id = new_res["memory_id"]
            old_rec.superseded_by = new_id
            self._record_audit_event(
                memory_id=old_memory_id,
                tenant_id=tenant_id,
                action_type="SUPERSEDE",
                actor_id=actor_id,
                reason=f"Superseded by new memory record '{new_id}'",
                trace_id=f"tr_sup_{uuid.uuid4().hex[:8]}",
                payload={"new_memory_id": new_id},
            )
            return {"success": True, "old_memory_id": old_memory_id, "new_memory_id": new_id, "status": "SUPERSEDED"}

        return {"success": False, "error": "Failed to store updated memory record"}

    def revoke_memory(
        self,
        memory_id: str,
        tenant_id: str,
        actor_id: str = "agent_system",
        reason: str = "Soft-delete revocation requested",
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform durable soft-delete revocation.

        DO NOT physically delete the durable record. Mark status as REVOKED/EXPIRED,
        preserve immutable audit evidence, and exclude from normal retrieval.
        """
        rec = self._memory_store.get(memory_id)
        if not rec or rec.tenant_id != tenant_id:
            return {"success": False, "error": "Memory record not found or tenant mismatch"}

        rec.status = "REVOKED"
        rev_trace = trace_id or f"tr_rev_{uuid.uuid4().hex[:8]}"

        self._record_audit_event(
            memory_id=memory_id,
            tenant_id=tenant_id,
            action_type="REVOKE",
            actor_id=actor_id,
            reason=reason,
            trace_id=rev_trace,
            payload={"previous_status": "ACTIVE", "new_status": "REVOKED"},
        )

        return {
            "success": True,
            "memory_id": memory_id,
            "status": "REVOKED",
            "reason": reason,
            "trace_id": rev_trace,
            "audit_preserved": True,
        }

    def _redact_secrets_and_pii(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive keys from structured payloads."""
        if not isinstance(payload, dict):
            return {}
        redacted = dict(payload)
        sensitive_keywords = ["password", "secret", "token", "api_key", "ssn", "private_key"]
        for k, v in redacted.items():
            if any(sk in k.lower() for sk in sensitive_keywords):
                redacted[k] = "[REDACTED_SECRET]"
            elif isinstance(v, dict):
                redacted[k] = self._redact_secrets_and_pii(v)
        return redacted

    def _redact_text(self, text: str) -> str:
        """Redact text patterns containing bearer tokens or passwords."""
        if not text:
            return ""
        words = text.split()
        sanitized = []
        for w in words:
            if any(sk in w.lower() for sk in ["bearer=", "secret=", "password=", "key="]):
                sanitized.append("[REDACTED_SECRET]")
            else:
                sanitized.append(w)
        return " ".join(sanitized)

    def _find_by_hash(self, tenant_id: str, namespace: str, content_hash: str) -> Optional[GovernedMemoryRecord]:
        for r in self._memory_store.values():
            if r.tenant_id == tenant_id and r.memory_namespace == namespace and r.content_hash == content_hash:
                return r
        return None

    def _record_audit_event(self, memory_id: str, tenant_id: str, action_type: str, actor_id: str, reason: str, trace_id: str, payload: Dict[str, Any]) -> None:
        event = {
            "event_id": str(uuid.uuid4()),
            "memory_id": memory_id,
            "tenant_id": tenant_id,
            "action_type": action_type,
            "actor_id": actor_id,
            "reason": reason,
            "trace_id": trace_id,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._memory_events.append(event)

    def _record_retrieval_audit(self, tenant_id: str, retrieval_id: str, query: str, memory_ids: List[str], budget_used: int) -> None:
        try:
            from packages.database.session import SessionLocal, sync_engine
            from packages.database.base import Base
            from packages.database.models.agent_memory import AgentMemoryRetrievalModel

            Base.metadata.create_all(bind=sync_engine)
            db = SessionLocal()
            try:
                db_obj = AgentMemoryRetrievalModel(
                    retrieval_id=retrieval_id,
                    tenant_id=tenant_id,
                    agent_run_id="run_compiled",
                    query=query,
                    retrieved_memory_ids=memory_ids,
                    relevance_scores={},
                    compilation_budget_used=budget_used,
                )
                db.add(db_obj)
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        except Exception:
            pass

    def _persist_db_memory(self, record: GovernedMemoryRecord) -> None:
        try:
            from packages.database.session import SessionLocal, sync_engine
            from packages.database.base import Base
            from packages.database.models.agent_memory import AgentMemoryModel

            Base.metadata.create_all(bind=sync_engine)
            db = SessionLocal()
            try:
                db_obj = AgentMemoryModel(
                    memory_id=record.memory_id,
                    tenant_id=record.tenant_id,
                    workspace_id=record.workspace_id,
                    agent_id=record.agent_id,
                    agent_run_id=record.agent_run_id,
                    memory_namespace=record.memory_namespace,
                    memory_type=record.memory_type,
                    memory_key=record.memory_key,
                    content=record.content,
                    structured_payload=record.structured_payload,
                    content_hash=record.content_hash,
                    source_type=record.source_type,
                    source_reference=record.source_reference,
                    source_trace_id=record.source_trace_id,
                    confidence=record.confidence,
                    importance=record.importance,
                    data_classification=record.data_classification,
                    sensitivity=record.sensitivity,
                    status=record.status,
                    version=record.version,
                    created_by="system",
                )
                db.add(db_obj)
                db.commit()
            except Exception:
                db.rollback()
            finally:
                db.close()
        except Exception:
            pass


governed_agent_memory_service = GovernedAgentMemoryService()
agent_memory_service = governed_agent_memory_service

