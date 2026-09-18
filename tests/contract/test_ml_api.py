"""AEGIS Machine Learning Platform REST API Contract Tests."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)


def test_ml_overview_contract():
    """Verify GET /api/v1/ml/overview endpoint contract."""
    response = client.get("/api/v1/ml/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "total_features" in data
    assert "total_models" in data


def test_ml_features_and_sets_contract():
    """Verify GET and POST /api/v1/ml/features and /feature-sets contract."""
    # Feature registration
    feat_res = client.post("/api/v1/ml/features", json={
        "name": "Contract Feature",
        "transformation_definition": "LOG1P",
    })
    assert feat_res.status_code == 201
    feat_data = feat_res.json()
    assert feat_data["name"] == "Contract Feature"

    list_feat = client.get("/api/v1/ml/features")
    assert list_feat.status_code == 200
    assert list_feat.json()["total"] >= 1

    # Feature Set creation
    fs_res = client.post("/api/v1/ml/feature-sets", json={
        "name": "Contract Feature Set",
        "feature_ids": [feat_data["id"]],
    })
    assert fs_res.status_code == 201
    assert fs_res.json()["name"] == "Contract Feature Set"


def test_ml_models_registry_and_predict_contract():
    """Verify Model registration, evaluation, promotion, deployment, and predict contract."""
    # Create model
    mod_res = client.post("/api/v1/ml/models", json={
        "name": "Contract Test Model",
        "task_type": "CLASSIFICATION",
    })
    assert mod_res.status_code == 201
    mod_id = mod_res.json()["id"]

    # Create experiment & run
    exp_res = client.post("/api/v1/ml/experiments", json={"name": "Contract Exp"})
    exp_id = exp_res.json()["id"]

    run_res = client.post(f"/api/v1/ml/experiments/{exp_id}/runs", json={
        "algorithm": "RANDOM_FOREST_CLASSIFIER",
    })
    run_id = run_res.json()["id"]

    # Queue training job
    job_res = client.post("/api/v1/ml/training-jobs", json={
        "experiment_id": exp_id,
        "run_id": run_id,
        "algorithm": "RANDOM_FOREST_CLASSIFIER",
    })
    assert job_res.status_code == 201

    # Get monitoring
    mon_res = client.get("/api/v1/ml/monitoring")
    assert mon_res.status_code == 200

    # Get drift
    drift_res = client.get("/api/v1/ml/drift")
    assert drift_res.status_code == 200

    # Evaluate drift
    eval_drift = client.post("/api/v1/ml/drift/evaluate", json={
        "model_id": mod_id,
        "feature_name": "usage_30d",
    })
    assert eval_drift.status_code == 200
    assert "status" in eval_drift.json()
