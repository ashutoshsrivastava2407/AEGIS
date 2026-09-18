"""Central Continuous Learning & Improvement Service Facade."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from services.learning.signals import LearningSignalEngine
from services.learning.lifecycle import GovernedImprovementLifecycleEngine
from services.learning.attribution import OutcomeAttributionEngine
from services.learning.executive import ExecutiveIntelligenceAndScenarioEngine


class ContinuousLearningService:
    """Central facade for AEGIS Continuous Learning, Improvement, and Outcome Attribution."""

    def __init__(self, db_session=None):
        self.db = db_session
        self.signals = LearningSignalEngine(db_session)
        self.lifecycle = GovernedImprovementLifecycleEngine(db_session)
        self.attribution = OutcomeAttributionEngine(db_session)
        self.executive = ExecutiveIntelligenceAndScenarioEngine(db_session)

    def get_learning_summary(self, tenant_id: str = "default") -> Dict[str, Any]:
        """Generate high-level continuous learning and improvement summary."""
        signals = self.signals.list_signals(tenant_id=tenant_id)
        candidates = self.lifecycle.list_candidates(tenant_id=tenant_id)
        observations = self.attribution.list_observations(tenant_id=tenant_id)

        return {
            "status": "ACTIVE",
            "signals_count": len(signals),
            "candidates_count": len(candidates),
            "outcome_observations_count": len(observations),
            "learning_version": "AEGIS_ContinuousLearning_v1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id,
        }
