"""AEGIS Machine Learning Platform REST API Router."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from packages.database.session import get_db
from services.ml.services import ml_service
from services.ml.registry.registry import InvalidModelLifecycleTransitionError
from services.ml.inference.predictor import InferenceError

router = APIRouter(prefix="/ml", tags=["ml"])

DEFAULT_TENANT_ID = "tenant-aegis-primary"


@router.get("/overview")
def get_ml_overview(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve ML platform executive operational overview."""
    return ml_service.get_overview(tenant_id, db)


# Features & Feature Sets
@router.get("/features")
def list_features(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List registered governed feature definitions."""
    features = ml_service.list_features(tenant_id, db)
    return {"features": features, "total": len(features)}


@router.post("/features", status_code=status.HTTP_201_CREATED)
def create_feature(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Register a new feature definition."""
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Feature 'name' is required.")
    return ml_service.create_feature(tenant_id, data, db)


@router.get("/feature-sets")
def list_feature_sets(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List feature set collections."""
    feature_sets = ml_service.list_feature_sets(tenant_id, db)
    return {"feature_sets": feature_sets, "total": len(feature_sets)}


@router.post("/feature-sets", status_code=status.HTTP_201_CREATED)
def create_feature_set(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a reproducible feature set."""
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="FeatureSet 'name' is required.")
    return ml_service.create_feature_set(tenant_id, data, db)


# Experiments & Runs
@router.get("/experiments")
def list_experiments(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List ML experiments."""
    experiments = ml_service.list_experiments(tenant_id, db)
    return {"experiments": experiments, "total": len(experiments)}


@router.post("/experiments", status_code=status.HTTP_201_CREATED)
def create_experiment(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new ML experiment."""
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Experiment 'name' is required.")
    return ml_service.create_experiment(tenant_id, data, db)


@router.get("/experiments/{experiment_id}/runs")
def list_experiment_runs(
    experiment_id: str,
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List runs under a specific experiment."""
    runs = ml_service.list_runs(tenant_id, experiment_id, db)
    return {"runs": runs, "total": len(runs)}


@router.post("/experiments/{experiment_id}/runs", status_code=status.HTTP_201_CREATED)
def create_experiment_run(
    experiment_id: str,
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Log an experiment run."""
    return ml_service.create_run(tenant_id, experiment_id, data, db)


# Training Jobs
@router.get("/training-jobs")
def list_training_jobs(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List training jobs."""
    jobs = ml_service.list_training_jobs(tenant_id, db)
    return {"training_jobs": jobs, "total": len(jobs)}


@router.post("/training-jobs", status_code=status.HTTP_201_CREATED)
def create_training_job(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Queue a model training job."""
    if not data.get("experiment_id") or not data.get("run_id"):
        raise HTTPException(status_code=400, detail="Fields 'experiment_id' and 'run_id' are required.")
    return ml_service.create_training_job(tenant_id, data, db)


# Models, Versions, Evaluations & Promotions
@router.get("/models")
def list_models(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List registered models."""
    models = ml_service.list_models(tenant_id, db)
    return {"models": models, "total": len(models)}


@router.post("/models", status_code=status.HTTP_201_CREATED)
def create_model(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Register a new model entity."""
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Model 'name' is required.")
    return ml_service.create_model(tenant_id, data, db)


@router.get("/models/{model_id}/versions")
def list_model_versions(
    model_id: str,
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List versions of a model."""
    versions = ml_service.list_model_versions(tenant_id, model_id, db)
    return {"versions": versions, "total": len(versions)}


@router.post("/models/{model_id}/versions/{version}/evaluate")
def evaluate_model_version(
    model_id: str,
    version: int,
    data: Optional[Dict[str, Any]] = None,
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Run formal evaluation on model version."""
    try:
        return ml_service.evaluate_version(tenant_id, model_id, version, data or {}, db)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.post("/models/{model_id}/versions/{version_id}/promote")
def promote_model_version(
    model_id: str,
    version_id: str,
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Promote model version through strict state transitions (DRAFT -> EVALUATED -> APPROVED -> STAGING -> PRODUCTION -> RETIRED)."""
    target_status = data.get("target_status")
    if not target_status:
        raise HTTPException(status_code=400, detail="Field 'target_status' is required.")
    try:
        return ml_service.promote_model_version(tenant_id, version_id, target_status, db)
    except InvalidModelLifecycleTransitionError as ie:
        raise HTTPException(status_code=400, detail=str(ie))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


# Deployments & Online Predict
@router.get("/deployments")
def list_deployments(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List active model deployments."""
    deployments = ml_service.list_deployments(tenant_id, db)
    return {"deployments": deployments, "total": len(deployments)}


@router.post("/deployments", status_code=status.HTTP_201_CREATED)
def create_deployment(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Deploy an APPROVED/STAGING/PRODUCTION model version."""
    if not data.get("model_version_id"):
        raise HTTPException(status_code=400, detail="Field 'model_version_id' is required.")
    try:
        return ml_service.create_deployment(tenant_id, data, db)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/models/{model_id}/versions/{version}/predict")
def predict_online(
    model_id: str,
    version: int,
    body: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Execute real online prediction inference against trained model artifact."""
    try:
        return ml_service.predict(tenant_id, model_id, version, body, db)
    except InferenceError as ie:
        raise HTTPException(status_code=400, detail=str(ie))


# Monitoring, Drift, Lineage & Retraining
@router.get("/monitoring")
def get_monitoring_stats(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get model monitoring & latency metrics."""
    return ml_service.get_monitoring(tenant_id, db)


@router.get("/drift")
def list_drift_records(
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """List feature & prediction drift evaluation records."""
    drifts = ml_service.list_drift_records(tenant_id, db)
    return {"drift_records": drifts, "total": len(drifts)}


@router.post("/drift/evaluate")
def evaluate_drift(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Execute statistical drift evaluation."""
    model_id = data.get("model_id", "model_default")
    feature_name = data.get("feature_name", "usage_30d")
    return ml_service.evaluate_drift(tenant_id, model_id, feature_name, db)


@router.get("/lineage/{version_id}")
def get_model_lineage(
    version_id: str,
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get ML entity lineage DAG."""
    return ml_service.get_lineage_dag(version_id, db)


@router.post("/retraining", status_code=status.HTTP_201_CREATED)
def trigger_retraining(
    data: Dict[str, Any],
    tenant_id: str = DEFAULT_TENANT_ID,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Trigger model retraining workflow."""
    model_id = data.get("model_id")
    if not model_id:
        raise HTTPException(status_code=400, detail="Field 'model_id' is required.")
    try:
        return ml_service.trigger_retraining(tenant_id, model_id, db)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
