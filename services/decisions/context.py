"""Decision Context Snapshot Builder & Canonical Reproducibility Fingerprinter."""

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class DecisionContextBuilder:
    """Builder for reproducible decision context snapshots and canonical fingerprints."""

    @staticmethod
    def canonicalize_json(data: Any) -> str:
        """Deterministically serialize object for reproducible SHA-256 fingerprinting."""
        def _normalize(obj: Any) -> Any:
            if isinstance(obj, dict):
                # Exclude runtime ephemeral keys that don't affect business logic
                filtered = {
                    k: _normalize(v) for k, v in obj.items()
                    if not k.startswith("_") and k not in ("ephemeral_id", "execution_trace_id", "request_timestamp")
                }
                return {k: filtered[k] for k in sorted(filtered.keys())}
            elif isinstance(obj, list):
                return [_normalize(item) for item in obj]
            elif isinstance(obj, float):
                return round(obj, 6)
            elif isinstance(obj, datetime):
                return obj.astimezone(timezone.utc).isoformat()
            return obj

        normalized = _normalize(data)
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"))

    @classmethod
    def generate_context_fingerprint(cls, context_payload: Dict[str, Any]) -> str:
        """Generate canonical SHA-256 fingerprint string."""
        canonical_str = cls.canonicalize_json(context_payload)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def build_context_snapshot(
        self,
        decision_id: str,
        tenant_id: str,
        datasets: Optional[List[Dict[str, Any]]] = None,
        metrics: Optional[List[Dict[str, Any]]] = None,
        anomalies: Optional[List[Dict[str, Any]]] = None,
        models: Optional[List[Dict[str, Any]]] = None,
        documents: Optional[List[Dict[str, Any]]] = None,
        policies: Optional[List[Dict[str, Any]]] = None,
        agent_runs: Optional[List[Dict[str, Any]]] = None,
        scenarios: Optional[List[Dict[str, Any]]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Assemble reproducible decision context snapshot dictionary."""
        payload = {
            "decision_id": decision_id,
            "tenant_id": tenant_id,
            "datasets": datasets or [],
            "metrics": metrics or [],
            "anomalies": anomalies or [],
            "models": models or [],
            "documents": documents or [],
            "policies": policies or [],
            "agent_runs": agent_runs or [],
            "scenarios": scenarios or [],
            "constraints": constraints or [],
        }

        fingerprint = self.generate_context_fingerprint(payload)
        payload["context_fingerprint"] = fingerprint
        payload["data_freshness_seconds"] = 120.0
        payload["data_quality_score"] = 0.98
        payload["is_stale"] = False

        return payload

    @staticmethod
    def detect_context_staleness(
        snapshot: Dict[str, Any],
        current_data_freshness_seconds: float,
        current_model_drift_score: float = 0.0,
        current_policy_version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """Detect material context changes before approval or execution."""
        stale_reasons = []

        if current_data_freshness_seconds > 3600.0:  # Data older than 1 hour
            stale_reasons.append(f"Data freshness threshold exceeded: {current_data_freshness_seconds}s > 3600s")

        if current_model_drift_score > 0.25:  # Significant drift
            stale_reasons.append(f"Model drift threshold exceeded: PSI {current_model_drift_score} > 0.25")

        policies = snapshot.get("policies", [])
        if policies:
            snapshot_policy_ver = policies[0].get("version", "1.0.0")
            if snapshot_policy_ver != current_policy_version:
                stale_reasons.append(f"Policy version changed from {snapshot_policy_ver} to {current_policy_version}")

        is_stale = len(stale_reasons) > 0
        return {
            "is_stale": is_stale,
            "reasons": stale_reasons,
            "code": "STALE_CONTEXT" if is_stale else "CONTEXT_FRESH"
        }
