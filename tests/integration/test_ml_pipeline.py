"""AEGIS Machine Learning End-to-End Pipeline Integration Test."""

import uuid
import pytest
import numpy as np
from packages.database.session import SessionLocal
from services.data_platform.services import data_platform_service
from services.ml.services import ml_service
from packages.security import UserContext


def test_end_to_end_ml_pipeline():
    tenant_id = f"tenant_ml_e2e_{uuid.uuid4().hex[:6]}"
    user = UserContext(
        user_id="usr_ml_engineer",
        tenant_id=tenant_id,
        username="ml_lead",
        email="ml@aegis.enterprise",
        is_admin=True,
    )
    db = SessionLocal()

    try:
        # Step 1: Register governed dataset in AEGIS Data Platform
        dataset_meta = ml_service.get_overview(tenant_id, db)
        assert dataset_meta is not None
        assert dataset_meta["status"] == "OPERATIONAL"

        # Step 2: Create versioned feature definitions
        f1 = ml_service.create_feature(tenant_id, {
            "name": "usage_30d",
            "transformation_definition": "LOG1P",
            "data_type": "FLOAT",
        }, db)
        assert f1["id"] is not None
        assert f1["version"] >= 1

        f2 = ml_service.create_feature(tenant_id, {
            "name": "avg_spend",
            "transformation_definition": "NORMALIZE_100",
            "data_type": "FLOAT",
        }, db)
        assert f2["id"] is not None

        # Step 3: Create feature set
        fs = ml_service.create_feature_set(tenant_id, {
            "name": "customer_churn_features_v1",
            "feature_ids": [f1["id"], f2["id"]],
            "purpose": "TRAINING",
        }, db)
        assert fs["id"] is not None

        # Step 4: Create experiment
        exp = ml_service.create_experiment(tenant_id, {
            "name": "Customer Churn Prediction Experiment",
            "objective": "Optimize F1 Score",
        }, db)
        assert exp["id"] is not None

        # Step 5: Execute real scikit-learn training job with deterministic data
        run = ml_service.create_run(tenant_id, exp["id"], {
            "algorithm": "RANDOM_FOREST_CLASSIFIER",
            "hyperparameters": {"n_estimators": 10, "max_depth": 3},
            "parameters": {"random_seed": 42},
            "status": "RUNNING",
        }, db)

        job = ml_service.create_training_job(tenant_id, {
            "experiment_id": exp["id"],
            "run_id": run["id"],
            "algorithm": "RANDOM_FOREST_CLASSIFIER",
            "feature_set_id": fs["id"],
            "configuration": {"hyperparameters": {"n_estimators": 10}, "random_seed": 42},
        }, db)
        assert job["id"] is not None

        # Execute training with real scikit-learn fit
        X_train = np.array([
            [10.0, 50.0], [12.0, 55.0], [5.0, 20.0], [15.0, 70.0],
            [2.0, 10.0], [1.0, 5.0], [20.0, 90.0], [3.0, 15.0]
        ])
        y_train = np.array([1, 1, 0, 1, 0, 0, 1, 0])

        model_entity = ml_service.create_model(tenant_id, {
            "name": "Customer Churn Model",
            "task_type": "CLASSIFICATION",
        }, db)
        assert model_entity["id"] is not None

        # Step 6 & 7: Register resulting model version and artifact reference
        from services.ml.training.trainer import TrainingEngine
        completed_job, trained_model_obj, artifact_meta = TrainingEngine.execute_job(
            session=db,
            job_id=job["id"],
            X_train=X_train,
            y_train=y_train,
            model_id=model_entity["id"],
            version=1,
        )
        assert completed_job.status == "COMPLETED"
        assert "checksum" in artifact_meta

        m_version = ml_service.create_model_version(
            tenant_id=tenant_id,
            model_id=model_entity["id"],
            experiment_run_id=run["id"],
            algorithm="RANDOM_FOREST_CLASSIFIER",
            hyperparameters={"n_estimators": 10},
            artifact_reference=artifact_meta,
            evaluation_summary={"primary_metric": "f1_score"},
            db=db,
        )
        assert m_version["status"] == "DRAFT"

        # Step 8: Evaluate model version (compute actual accuracy, precision, recall, f1)
        eval_res = ml_service.evaluate_version(tenant_id, model_entity["id"], 1, {}, db)
        assert "metrics" in eval_res
        assert "f1_score" in eval_res["metrics"]

        # Step 9: Promote through valid registry lifecycle (EVALUATED -> APPROVED -> PRODUCTION)
        p_appr = ml_service.promote_model_version(tenant_id, m_version["id"], "APPROVED", db)
        assert p_appr["status"] == "APPROVED"

        p_prod = ml_service.promote_model_version(tenant_id, m_version["id"], "PRODUCTION", db)
        assert p_prod["status"] == "PRODUCTION"

        # Step 10: Create active deployment record
        dep = ml_service.create_deployment(tenant_id, {
            "model_version_id": m_version["id"],
            "environment": "PRODUCTION",
        }, db)
        assert dep["status"] == "ACTIVE"
        assert "/predict" in dep["endpoint_reference"]

        # Step 11 & 12: Execute real online predict call against trained model binary
        predict_res = ml_service.predict(tenant_id, model_entity["id"], 1, {
            "features": [12.0, 60.0]
        }, db)
        assert "prediction" in predict_res
        assert predict_res["latency_ms"] >= 0.0

        # Step 13: Run monitoring calculations
        mon = ml_service.get_monitoring(tenant_id, db)
        assert mon["total_predictions"] >= 1
        assert mon["status"] == "HEALTHY"

        # Step 14: Run drift evaluation (PSI score)
        drift_res = ml_service.evaluate_drift(tenant_id, model_entity["id"], "usage_30d", db)
        assert drift_res["status"] in ("NO_DRIFT", "DRIFT_DETECTED")

        # Step 15: Verify model lineage DAG
        lineage = ml_service.get_lineage_dag(m_version["id"], db)
        assert len(lineage["nodes"]) >= 5
        assert len(lineage["edges"]) >= 4

        # Step 16 & 17: Retraining trigger & tenant boundary check
        retrain_res = ml_service.trigger_retraining(tenant_id, model_entity["id"], db)
        assert retrain_res["promotion_gate"] == "EXPLICIT_APPROVAL_REQUIRED"

        # Step 18: Tenant Boundary Isolation Verification
        isolated_models = ml_service.list_models("tenant_other_unauthorized", db)
        assert len(isolated_models) == 0

    finally:
        db.close()
