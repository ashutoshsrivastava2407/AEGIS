"""Governed Continuous Learning Improvement Candidate Lifecycle Engine."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from services.security.policy_engine import ServerPolicyEngine
from packages.database.models.command_learning import ImprovementCandidateModel


class GovernedImprovementLifecycleEngine:
    """Manages improvement candidate progression under Step 10 policy governance."""

    VALID_STAGES = [
        "OBSERVED",
        "CANDIDATE",
        "EVALUATING",
        "VALIDATED",
        "APPROVED",
        "SHADOW",
        "PROMOTED",
        "MONITORED",
        "ROLLED_BACK",
    ]

    def __init__(self, db_session=None):
        self.db = db_session
        self.policy_engine = ServerPolicyEngine()
        self._candidates: Dict[str, Dict[str, Any]] = {}

    def propose_candidate(
        self,
        title: str,
        target_subsystem: str,
        description: str,
        proposal: Dict[str, Any],
        actor_id: str = "ContinuousLearningEngine",
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Propose a new continuous learning improvement candidate."""
        candidate_id = f"cand-{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()

        candidate = {
            "id": candidate_id,
            "candidate_id": candidate_id,
            "title": title,
            "target_subsystem": target_subsystem.upper(),
            "description": description,
            "status": "OBSERVED",
            "proposal_json": proposal,
            "evaluation_result_json": {},
            "policy_evaluation_id": None,
            "approval_id": None,
            "promoted_at": None,
            "tenant_id": tenant_id,
            "created_at": now_str,
        }

        self._candidates[candidate_id] = candidate

        if self.db:
            model = ImprovementCandidateModel(
                id=str(uuid.uuid4()),
                candidate_id=candidate_id,
                target_subsystem=target_subsystem.upper(),
                title=title,
                description=description,
                status="OBSERVED",
                proposal_json=proposal,
                evaluation_result_json={},
                tenant_id=tenant_id,
            )
            self.db.add(model)
            self.db.commit()

        return candidate

    def transition_candidate(
        self,
        candidate_id: str,
        target_status: str,
        actor_id: str = "LearningGovernanceOperator",
        tenant_id: str = "default",
        user_role: str = "ENTERPRISE_ADMIN",
    ) -> Dict[str, Any]:
        """Transition candidate stage, evaluating Step 10 server-authoritative policy for promotion."""
        status_upper = target_status.upper()
        if status_upper not in self.VALID_STAGES:
            raise ValueError(f"Invalid candidate status '{target_status}'. Allowed: {self.VALID_STAGES}")

        candidate = self._candidates.get(candidate_id)
        if not candidate:
            candidate = {
                "candidate_id": candidate_id,
                "title": f"Candidate {candidate_id}",
                "target_subsystem": "ML",
                "status": "OBSERVED",
                "proposal_json": {},
                "tenant_id": tenant_id,
            }
            self._candidates[candidate_id] = candidate

        # Evaluate Step 10 Policy Engine when approving or promoting
        if status_upper in ["APPROVED", "PROMOTED"]:
            policy_res = self.policy_engine.evaluate_policy(
                subject_id=actor_id,
                resource_id=candidate_id,
                action=f"PROMOTE_LEARNING_CANDIDATE_{status_upper}",
                context={
                    "user_role": user_role,
                    "target_subsystem": candidate.get("target_subsystem"),
                    "risk_level": "CRITICAL",
                },
                tenant_id=tenant_id,
            )
            policy_decision = policy_res.get("decision", "DENY")
            if policy_decision not in ["ALLOW"]:
                candidate["policy_evaluation_id"] = policy_res.get("evaluation_id")
                candidate["status"] = "BLOCKED_BY_POLICY"
                return candidate

            candidate["policy_evaluation_id"] = policy_res.get("evaluation_id")

        now_str = datetime.now(timezone.utc).isoformat()
        candidate["status"] = status_upper
        if status_upper == "PROMOTED":
            candidate["promoted_at"] = now_str

        if self.db:
            db_cand = self.db.query(ImprovementCandidateModel).filter_by(candidate_id=candidate_id).first()
            if db_cand:
                db_cand.status = status_upper
                if status_upper == "PROMOTED":
                    db_cand.promoted_at = now_str
                self.db.commit()

        return candidate

    def list_candidates(
        self,
        target_subsystem: Optional[str] = None,
        status: Optional[str] = None,
        tenant_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """List historical and active improvement candidates."""
        candidates = list(self._candidates.values())
        if target_subsystem:
            candidates = [c for c in candidates if c.get("target_subsystem") == target_subsystem.upper()]
        if status:
            candidates = [c for c in candidates if c.get("status") == status.upper()]
        return candidates
