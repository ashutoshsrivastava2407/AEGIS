"""Unit Tests for AEGIS Machine Learning Subsystem."""

import os
import pytest
import numpy as np
from services.ml.features.transformations import FeatureTransformer, FeatureTransformationError
from services.ml.features.leakage_guard import LeakageGuard, DataLeakageValidationError
from services.ml.training.models_provider import ModelProviderFactory, ModelProviderError
from services.ml.training.artifact_store import artifact_store
from services.ml.registry.registry import ModelRegistryEngine, InvalidModelLifecycleTransitionError
from services.ml.monitoring.drift_detector import DriftDetector
from packages.database.session import SessionLocal
from packages.database.models.ml_model import ModelModel, ModelVersionModel


def test_feature_transformations():
    """Verify deterministic numerical, categorical, and temporal feature transformations."""
    assert FeatureTransformer.apply_numerical(100.0, "NORMALIZE_100") == 1.0
    assert FeatureTransformer.apply_numerical(0.0, "LOG1P") == 0.0
    assert FeatureTransformer.apply_numerical(5.0, "SQUARE") == 25.0

    assert FeatureTransformer.apply_categorical(" Premium_User ", "LABEL") is not None
    assert FeatureTransformer.apply_temporal("2026-09-18T14:30:00Z", "HOUR") == 14


def test_leakage_guard_target_leakage():
    """Verify LeakageGuard flags target leakage when target is in feature set."""
    features = ["usage_30d", "avg_spend", "target_churn"]
    
    with pytest.raises(DataLeakageValidationError):
        LeakageGuard.validate_target_leakage(features, target_column="target_churn")


def test_scikit_learn_model_provider_reproducibility():
    """Verify ModelProviderFactory trains real scikit-learn models with seed reproducibility."""
    X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0], [9.0, 10.0]])
    y = np.array([0, 0, 1, 1, 1])

    model1, meta1 = ModelProviderFactory.train_model(
        algorithm="RANDOM_FOREST_CLASSIFIER",
        X=X,
        y=y,
        hyperparameters={"n_estimators": 10},
        random_seed=42,
    )
    pred1 = model1.predict(X)

    model2, meta2 = ModelProviderFactory.train_model(
        algorithm="RANDOM_FOREST_CLASSIFIER",
        X=X,
        y=y,
        hyperparameters={"n_estimators": 10},
        random_seed=42,
    )
    pred2 = model2.predict(X)

    np.testing.assert_array_equal(pred1, pred2)
    assert meta1["task_type"] == "CLASSIFICATION"


def test_artifact_store_checksum_integrity():
    """Verify ModelArtifactStore computes and verifies SHA-256 checksums."""
    model_dummy = {"weights": [0.1, 0.5, 0.9]}
    meta = artifact_store.save_artifact(model_dummy, model_id="test_m1", version=1)

    assert "checksum" in meta
    assert os.path.exists(meta["uri"])

    loaded = artifact_store.load_artifact(meta)
    assert loaded["weights"] == [0.1, 0.5, 0.9]


def test_model_registry_lifecycle_state_machine():
    """Verify strict model version promotion lifecycle state machine transitions."""
    db = SessionLocal()
    tenant_id = "tenant_registry_test"

    try:
        model = ModelRegistryEngine.register_model(db, tenant_id, "Registry Test Model")
        version = ModelRegistryEngine.create_model_version(
            session=db,
            tenant_id=tenant_id,
            model_id=model.id,
            experiment_run_id="run_1",
            algorithm="LogisticRegression",
            hyperparameters={"C": 1.0},
            artifact_reference={"checksum": "abc"},
            evaluation_summary={"f1": 0.9},
        )

        assert version.status == "DRAFT"

        # Invalid transition DRAFT -> PRODUCTION must raise InvalidModelLifecycleTransitionError
        with pytest.raises(InvalidModelLifecycleTransitionError):
            ModelRegistryEngine.promote_model_version(db, tenant_id, version.id, "PRODUCTION")

        # Valid transition chain: DRAFT -> EVALUATED -> APPROVED -> PRODUCTION
        v_eval = ModelRegistryEngine.promote_model_version(db, tenant_id, version.id, "EVALUATED")
        assert v_eval.status == "EVALUATED"

        v_appr = ModelRegistryEngine.promote_model_version(db, tenant_id, version.id, "APPROVED")
        assert v_appr.status == "APPROVED"

        v_prod = ModelRegistryEngine.promote_model_version(db, tenant_id, version.id, "PRODUCTION")
        assert v_prod.status == "PRODUCTION"

    finally:
        db.close()


def test_psi_drift_detector():
    """Verify Population Stability Index (PSI) drift calculation."""
    ref_data = np.array([10.0, 10.5, 11.0, 10.2, 9.8, 10.1])
    same_data = np.array([10.1, 10.3, 10.9, 10.0, 9.9, 10.2])
    shifted_data = np.array([100.0, 105.0, 110.0, 102.0, 98.0, 101.0])

    psi_low = DriftDetector.calculate_psi(ref_data, same_data)
    psi_high = DriftDetector.calculate_psi(ref_data, shifted_data)

    assert psi_low < 0.1
    assert psi_high > 0.1
