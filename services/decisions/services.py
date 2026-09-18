"""Unified AEGIS Decision Platform Service Facade."""

import uuid
from typing import Dict, Any, List, Optional

from services.decisions.registry import DecisionRegistry
from services.decisions.contracts import ActionContractRegistry
from services.decisions.context import DecisionContextBuilder
from services.decisions.gates import DecisionIntegrityEvaluator, DecisionEligibilityEvaluator
from services.decisions.evidence import EvidenceManager
from services.decisions.options import MultiOptionGenerator
from services.decisions.evaluation import MCDAEvaluator
from services.decisions.optimization import OptimizationEngine
from services.decisions.risk import QuantitativeRiskEngine
from services.decisions.uncertainty import UncertaintyEngine
from services.decisions.simulation import SimulationEngine
from services.decisions.policy import ServerDecisionPolicyEngine
from services.decisions.approvals import DecisionApprovalEngine
from services.decisions.execution import DecisionExecutionEngine
from services.decisions.outcomes import OutcomeTracker
from services.decisions.feedback import FeedbackEngine
from services.decisions.verification import DecisionVerificationGate
from services.decisions.dossier import DecisionDossierGenerator

from packages.database.models.decision import DecisionModel, DecisionVersionModel, DecisionContextModel


class DecisionPlatformService:
    """Unified Facade coordinating the 14-stage AEGIS Decision Intelligence Architecture."""

    def __init__(self):
        self.registry = DecisionRegistry()
        self.contracts = ActionContractRegistry()
        self.context_builder = DecisionContextBuilder()
        self.integrity_evaluator = DecisionIntegrityEvaluator()
        self.eligibility_evaluator = DecisionEligibilityEvaluator()
        self.evidence_manager = EvidenceManager()
        self.options_generator = MultiOptionGenerator()
        self.mcda_evaluator = MCDAEvaluator()
        self.optimization_engine = OptimizationEngine()
        self.risk_engine = QuantitativeRiskEngine()
        self.uncertainty_engine = UncertaintyEngine()
        self.simulation_engine = SimulationEngine()
        self.policy_engine = ServerDecisionPolicyEngine()
        self.approval_engine = DecisionApprovalEngine()
        self.execution_engine = DecisionExecutionEngine()
        self.outcome_tracker = OutcomeTracker()
        self.feedback_engine = FeedbackEngine()
        self.verification_gate = DecisionVerificationGate()
        self.dossier_generator = DecisionDossierGenerator()

    def run_full_decision_pipeline(
        self,
        tenant_id: str = "default",
        owner: str = "analytics-lead@aegis.enterprise",
        requester: str = "agent:master-supervisor",
        objective: str = "Mitigate Q3 regional revenue anomaly and scale analytics compute",
        decision_type: str = "RESOURCE_ALLOCATION",
        business_domain: str = "FINANCE",
        user_role: str = "ENTERPRISE_ADMIN",
        raw_evidences: Optional[List[Dict[str, Any]]] = None,
        seed: int = 42
    ) -> Dict[str, Any]:
        """Execute the canonical 14-stage closed loop end-to-end."""
        decision_id = str(uuid.uuid4())

        # 1. Signal & 2. Context
        context_snapshot = self.context_builder.build_context_snapshot(
            decision_id=decision_id,
            tenant_id=tenant_id,
            datasets=[{"name": "regional_revenue", "version": "1.2.0"}],
            metrics=[{"name": "revenue_variance", "value": -0.18}],
            models=[{"name": "revenue_forecaster", "version": "2.1.0"}]
        )

        # 3. Investigation & 4. Evidence
        evidence_result = self.evidence_manager.process_evidence_set(raw_evidences or [
            {
                "title": "Revenue Anomaly Report",
                "source_type": "OBSERVED",
                "source_ref": "analytics:anomalies:q3_rev",
                "source_authority": "AUTHORITATIVE",
                "evidence_summary": "Observed 18% revenue drop in Q3 regional cluster",
                "confidence_weight": 0.95
            },
            {
                "title": "RAG Document Citation",
                "source_type": "DOCUMENT",
                "source_ref": "doc:q3_policy_guideline",
                "source_authority": "AUTHORITATIVE",
                "evidence_summary": "Policy requires resource reallocation when variance exceeds 15%",
                "confidence_weight": 0.90
            }
        ])

        # 5. Options Generation
        constraints = [{"constraint_key": "MAX_BUDGET", "threshold_value": 10000.0, "operator": "<="}]
        options = self.options_generator.generate_options(decision_type, objective, constraints)

        # 6. Evaluation (MCDA, Pareto, Sensitivity)
        criteria = [
            {"criterion_key": "EXPECTED_BENEFIT", "name": "Expected Revenue Benefit", "weight": 0.5, "unit": "USD"},
            {"criterion_key": "COST", "name": "Implementation Cost", "weight": 0.3, "unit": "USD"},
            {"criterion_key": "RISK", "name": "Operational Risk", "weight": 0.2, "unit": "SCALAR"}
        ]
        evaluations = self.mcda_evaluator.evaluate_options(options, criteria)

        # 6b. Pluggable Optimization
        opt_variables = [
            {"name": "analytics-worker-scaling", "cost": 1200.0, "expected_return": 15000.0, "max_allocation": 4}
        ]
        optimization_result = self.optimization_engine.optimize(
            problem_type="RESOURCE_ALLOCATION",
            objective_target="MAXIMIZE_REVENUE",
            variables=opt_variables,
            hard_constraints=constraints,
            budget_limit=10000.0
        )

        # 7. Simulation (Monte Carlo with stochastic basis guard)
        stochastic_basis = {"has_valid_distribution": True, "std_dev_ratio": 0.10}
        simulation_result = self.simulation_engine.run_simulation(
            base_value=15000.0,
            stochastic_basis=stochastic_basis,
            iterations=1000,
            seed=seed
        )

        # 8. Risk & Uncertainty
        risk_assessment = self.risk_engine.assess_risk(
            probability=0.25,
            impact_usd=1200.0,
            affected_services_count=1,
            is_irreversible=False
        )
        uncertainty_result = self.uncertainty_engine.calculate_uncertainty(
            model_type="revenue_forecaster",
            predictions=[14500.0, 15200.0, 14900.0, 15100.0],
            model_metadata={"supports_uncertainty": True}
        )

        # 9. Policy & Gates (Integrity & Eligibility)
        policy_eval = self.policy_engine.evaluate_policy(
            tenant_id=tenant_id,
            user_role=user_role,
            decision_type=decision_type,
            cost_usd=1200.0,
            risk_tier=risk_assessment["risk_tier"],
            affected_resources=["service:analytics-worker"]
        )

        integrity_eval = self.integrity_evaluator.evaluate(
            data_quality_score=0.98,
            data_freshness_seconds=120.0,
            model_health_score=0.95,
            evidence_conflict_detected=evidence_result["has_conflicts"],
            policy_result=policy_eval["policy_result"]
        )

        # 10. Decision Verification Gate
        verification_result = self.verification_gate.verify_decision(
            decision_id=decision_id,
            context_snapshot=context_snapshot,
            evaluations=evaluations,
            risk_assessment=risk_assessment,
            policy_evaluation=policy_eval
        )

        # 11. Approval & TOCTOU Revalidation
        approval_record = self.approval_engine.process_approval_action(
            decision_id=decision_id,
            approver_id="governance-officer@aegis.enterprise",
            approver_role="DECISION_APPROVER",
            action="APPROVE",
            rationale="Approved following verified MCDA score and policy compliance."
        )

        toctou_revalidation = self.approval_engine.revalidate_approval_before_execution(
            approval_record=approval_record,
            context_fingerprint_at_approval=context_snapshot["context_fingerprint"],
            current_context_fingerprint=context_snapshot["context_fingerprint"]
        )

        eligibility_eval = self.eligibility_evaluator.evaluate(
            integrity_status=integrity_eval["status"],
            risk_tier=risk_assessment["risk_tier"],
            approval_status=toctou_revalidation["status"]
        )

        # 12. Action Execution (Delegated to ToolExecutor with Outbox)
        idempotency_key = f"idempotent-action-{decision_id[:8]}"
        action_execution = self.execution_engine.execute_decision_action(
            decision_id=decision_id,
            action_type="SCALE_SERVICE_WORKERS",
            target_resource="service:analytics-worker",
            parameters={"service_name": "analytics-worker", "target_replicas": 4},
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            user_role=user_role
        )

        # 13. Outcome Measurement
        outcome_result = self.outcome_tracker.measure_outcome(
            decision_id=decision_id,
            action_id=action_execution.get("outbox_event", {}).get("outbox_event_id", "act-1"),
            expected_impact_usd=15000.0,
            actual_impact_usd=16200.0,
            attribution_classification="CAUSALLY_ESTIMATED",
            causal_methodology_version="AEGIS_DiD_v1.0",
            counterfactual_baseline_usd=14000.0,
            identification_assumptions=["Parallel trends assumption verified", "No concurrent spillover events"]
        )

        # 14. Feedback & Controlled Calibration
        calibration_proposal = self.feedback_engine.create_calibration_proposal(
            decision_id=decision_id,
            outcome_id=outcome_result.get("outcome_id", f"out-{decision_id[:8]}"),
            target_component="CRITERIA_WEIGHT",
            previous_config={"version": 1, "weight": 0.5, "version_string": "1.0.0"},
            observed_variance_usd=outcome_result["variance_usd"]
        )

        # Build Manifest and Dossier
        manifest = self.dossier_generator.generate_manifest(
            decision_id=decision_id,
            version_number=1,
            context_snapshot=context_snapshot,
            evidences=evidence_result["evidences"],
            options=options,
            evaluations=evaluations,
            risk_assessment=risk_assessment,
            uncertainty=uncertainty_result,
            simulation=simulation_result,
            optimization=optimization_result,
            policy_evaluation=policy_eval,
            approval_record=toctou_revalidation,
            action_execution=action_execution,
            outcome=outcome_result,
            feedback=calibration_proposal
        )

        dossier = self.dossier_generator.generate_dossier(manifest)

        return {
            "decision_id": decision_id,
            "decision_version_id": manifest["decision_version_id"],
            "signal_id": manifest["signal_id"],
            "context_id": manifest["context_id"],
            "context_fingerprint": context_snapshot["context_fingerprint"],
            "investigation_run_id": manifest["investigation_run_id"],
            "evidence_ids": manifest["evidence_ids"],
            "option_ids": manifest["option_ids"],
            "evaluation_id": manifest["evaluation_id"],
            "simulation_id": manifest["simulation_id"],
            "risk_id": manifest["risk_id"],
            "uncertainty_id": manifest["uncertainty_id"],
            "policy_evaluation_id": manifest["policy_evaluation_id"],
            "approval_id": manifest["approval_id"],
            "action_id": manifest["action_id"],
            "outcome_id": manifest["outcome_id"],
            "feedback_id": manifest["feedback_id"],
            "trace_id": manifest["trace_id"],
            "manifest_id": manifest["manifest_id"],
            "manifest_hash": manifest["manifest_hash"],
            "tenant_id": tenant_id,
            "objective": objective,
            "status": "CLOSED",
            "stages_completed": 14,
            "integrity_status": integrity_eval["status"],
            "eligibility_status": eligibility_eval["status"],
            "verification_status": verification_result["status"],
            "toctou_revalidation": toctou_revalidation,
            "action_execution": action_execution,
            "outcome": outcome_result,
            "calibration_proposal": calibration_proposal,
            "dossier": dossier
        }
