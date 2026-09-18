"""AEGIS Real Model Inference Engine."""

from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session

from packages.database.models.ml_model import ModelVersionModel, ModelModel
from packages.database.models.ml_inference import ModelInferenceLogModel
from services.ml.training.artifact_store import artifact_store

logger = logging.getLogger("aegis.ml.inference")


class InferenceError(Exception):
    """Raised when online or batch prediction fails."""
    pass


class InferenceEngine:
    """Executes real model predictions and logs audit & latency metrics."""

    @staticmethod
    def predict_online(
        session: Session,
        tenant_id: str,
        model_id: str,
        version: int,
        input_data: Dict[str, Any],
        feature_set_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute real online prediction call against deployed model artifact."""
        start_time = time.time()

        m_version = session.query(ModelVersionModel).filter(
            ModelVersionModel.model_id == model_id,
            ModelVersionModel.version == version,
            ModelVersionModel.tenant_id == tenant_id
        ).first()

        if not m_version:
            raise InferenceError(f"ModelVersion v{version} for model '{model_id}' not found for tenant '{tenant_id}'.")

        artifact_meta = m_version.artifact_reference_json
        if not artifact_meta or "uri" not in artifact_meta:
            raise InferenceError(f"No artifact reference found for ModelVersion v{version}.")

        try:
            # Load real trained model binary
            model_obj = artifact_store.load_artifact(artifact_meta)

            # Extract features from input dict
            features = input_data.get("features", input_data)
            if isinstance(features, dict):
                feature_vals = [float(v) for v in features.values() if isinstance(v, (int, float, bool))]
            elif isinstance(features, list):
                feature_vals = [float(v) for v in features]
            else:
                feature_vals = [1.0]

            if not feature_vals:
                feature_vals = [1.0]

            X = np.array([feature_vals])
            raw_pred = model_obj.predict(X)

            # Format prediction output
            if hasattr(raw_pred, "tolist"):
                pred_val = raw_pred.tolist()
            else:
                pred_val = list(raw_pred)

            latency_ms = round((time.time() - start_time) * 1000.0, 2)

            prediction_result = {
                "prediction": pred_val[0] if len(pred_val) == 1 else pred_val,
                "model_id": model_id,
                "version": version,
                "algorithm": m_version.algorithm,
                "latency_ms": latency_ms,
            }

            # Record inference log
            log = ModelInferenceLogModel(
                tenant_id=tenant_id,
                model_version_id=m_version.id,
                feature_set_id=feature_set_id,
                inference_type="ONLINE",
                input_payload_json=input_data,
                prediction_result_json=prediction_result,
                latency_ms=latency_ms,
                status="SUCCESS",
            )
            session.add(log)
            session.commit()

            return prediction_result

        except Exception as e:
            latency_ms = round((time.time() - start_time) * 1000.0, 2)
            log = ModelInferenceLogModel(
                tenant_id=tenant_id,
                model_version_id=m_version.id if m_version else "unknown",
                inference_type="ONLINE",
                input_payload_json=input_data,
                prediction_result_json={},
                latency_ms=latency_ms,
                status="FAILED",
                error_message=str(e),
            )
            session.add(log)
            session.commit()
            raise InferenceError(f"Inference execution failed: {str(e)}")

    @staticmethod
    def execute_batch_inference(
        session: Session,
        tenant_id: str,
        model_version_id: str,
        input_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute batch predictions across a set of input records."""
        start_time = time.time()

        m_version = session.query(ModelVersionModel).filter(
            ModelVersionModel.id == model_version_id,
            ModelVersionModel.tenant_id == tenant_id
        ).first()

        if not m_version:
            raise InferenceError(f"ModelVersion id '{model_version_id}' not found.")

        model_obj = artifact_store.load_artifact(m_version.artifact_reference_json)

        predictions = []
        for record in input_records:
            vals = [float(v) for k, v in record.items() if isinstance(v, (int, float, bool))]
            if not vals:
                vals = [1.0]
            pred = model_obj.predict(np.array([vals]))[0]
            predictions.append({"record": record, "prediction": float(pred) if isinstance(pred, (np.number, float)) else int(pred)})

        latency_ms = round((time.time() - start_time) * 1000.0, 2)

        batch_log = ModelInferenceLogModel(
            tenant_id=tenant_id,
            model_version_id=m_version.id,
            inference_type="BATCH",
            input_payload_json={"total_records": len(input_records)},
            prediction_result_json={"processed_count": len(predictions)},
            latency_ms=latency_ms,
            status="SUCCESS",
        )
        session.add(batch_log)
        session.commit()

        return {
            "model_version_id": model_version_id,
            "processed_records": len(predictions),
            "latency_ms": latency_ms,
            "predictions": predictions,
        }
