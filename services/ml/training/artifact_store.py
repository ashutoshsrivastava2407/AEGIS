"""AEGIS Model Artifact Store Abstraction."""

import hashlib
import json
import os
from typing import Any, Dict, Tuple
import joblib


class ModelArtifactStore:
    """Manages serialized model binary artifacts, checksum verification, and storage metadata."""

    def __init__(self, base_dir: str = "data/ml_artifacts"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_artifact(self, model_obj: Any, model_id: str, version: int) -> Dict[str, Any]:
        """Serialize model object, compute SHA-256 checksum, and write to storage path."""
        file_name = f"model_{model_id}_v{version}.joblib"
        file_path = os.path.join(self.base_dir, file_name)

        joblib.dump(model_obj, file_path)

        # Compute SHA-256 checksum
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        checksum = hasher.hexdigest()
        size_bytes = os.path.getsize(file_path)

        metadata = {
            "uri": file_path,
            "filename": file_name,
            "checksum": checksum,
            "size_bytes": size_bytes,
            "format": "JOBLIB",
        }
        return metadata

    def load_artifact(self, artifact_metadata: Dict[str, Any]) -> Any:
        """Load serialized model object and verify SHA-256 checksum integrity."""
        uri = artifact_metadata.get("uri")
        expected_checksum = artifact_metadata.get("checksum")

        if not uri or not os.path.exists(uri):
            raise FileNotFoundError(f"Model artifact file not found at '{uri}'")

        # Verify checksum
        hasher = hashlib.sha256()
        with open(uri, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        actual_checksum = hasher.hexdigest()

        if expected_checksum and actual_checksum != expected_checksum:
            raise ValueError(f"Artifact checksum mismatch! Expected: {expected_checksum}, Actual: {actual_checksum}")

        return joblib.load(uri)


# Global artifact store instance
artifact_store = ModelArtifactStore()
