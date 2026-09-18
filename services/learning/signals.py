"""Continuous Learning Operational Signal Engine."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from packages.database.models.command_learning import LearningSignalModel


class LearningSignalEngine:
    """Tracks operational performance and learning signals across all AEGIS subsystems."""

    DIMENSIONS = ["DATA", "ML", "RAG", "AGENT", "DECISION", "WORKFLOW", "OPERATIONS"]

    def __init__(self, db_session=None):
        self.db = db_session
        self._signals: List[Dict[str, Any]] = []

    def record_signal(
        self,
        dimension: str,
        signal_type: str,
        source_component: str,
        payload: Dict[str, Any],
        severity: str = "MEDIUM",
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Record an operational learning signal."""
        dim_upper = dimension.upper()
        if dim_upper not in self.DIMENSIONS:
            dim_upper = "OPERATIONS"

        signal_id = f"sig-{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        signal_data = {
            "id": signal_id,
            "signal_id": signal_id,
            "dimension": dim_upper,
            "signal_type": signal_type,
            "source_component": source_component,
            "severity": severity.upper(),
            "payload_json": payload,
            "detected_at": now_str,
            "tenant_id": tenant_id,
        }

        self._signals.append(signal_data)

        if self.db:
            model = LearningSignalModel(
                id=str(uuid.uuid4()),
                signal_id=signal_id,
                dimension=dim_upper,
                signal_type=signal_type,
                source_component=source_component,
                severity=severity.upper(),
                payload_json=payload,
                detected_at=now_str,
                tenant_id=tenant_id,
            )
            self.db.add(model)
            self.db.commit()

        return signal_data

    def list_signals(
        self,
        dimension: Optional[str] = None,
        severity: Optional[str] = None,
        tenant_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """List operational learning signals."""
        results = [
            s for s in self._signals
            if s.get("tenant_id", "default") == tenant_id
        ]
        if dimension:
            results = [s for s in results if s.get("dimension") == dimension.upper()]
        if severity:
            results = [s for s in results if s.get("severity") == severity.upper()]
        return results or list(self._signals)
