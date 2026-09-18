"""AEGIS Modular Scikit-Learn Model Provider."""

import numpy as np
from typing import Any, Dict, List, Tuple
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest


class ModelProviderError(Exception):
    """Raised when model provider configuration or fitting fails."""
    pass


class ModelProviderFactory:
    """Factory creating and fitting production scikit-learn model instances."""

    SUPPORTED_ALGORITHMS = {
        "LOGISTIC_REGRESSION": "CLASSIFICATION",
        "RANDOM_FOREST_CLASSIFIER": "CLASSIFICATION",
        "LINEAR_REGRESSION": "REGRESSION",
        "RANDOM_FOREST_REGRESSOR": "REGRESSION",
        "ISOLATION_FOREST": "ANOMALY_DETECTION",
        "FORECASTING_REGRESSOR": "FORECASTING",
    }

    @classmethod
    def train_model(
        cls,
        algorithm: str,
        X: np.ndarray,
        y: np.ndarray,
        hyperparameters: Dict[str, Any],
        random_seed: int = 42
    ) -> Tuple[Any, Dict[str, Any]]:
        """Fit real scikit-learn model with explicit random seed and hyperparameters."""
        alg_upper = algorithm.upper().replace(" ", "_")

        if alg_upper not in cls.SUPPORTED_ALGORITHMS:
            # Fallback mapping
            if "CLASSIF" in alg_upper or "LOGISTIC" in alg_upper:
                alg_upper = "RANDOM_FOREST_CLASSIFIER"
            elif "REGRESS" in alg_upper or "LINEAR" in alg_upper:
                alg_upper = "RANDOM_FOREST_REGRESSOR"
            elif "ISOLATION" in alg_upper or "ANOMALY" in alg_upper:
                alg_upper = "ISOLATION_FOREST"
            else:
                alg_upper = "RANDOM_FOREST_CLASSIFIER"

        task_type = cls.SUPPORTED_ALGORITHMS[alg_upper]

        if alg_upper == "LOGISTIC_REGRESSION":
            model = LogisticRegression(
                C=float(hyperparameters.get("C", 1.0)),
                max_iter=int(hyperparameters.get("max_iter", 100)),
                random_state=random_seed
            )
            model.fit(X, y)

        elif alg_upper == "RANDOM_FOREST_CLASSIFIER":
            model = RandomForestClassifier(
                n_estimators=int(hyperparameters.get("n_estimators", 10)),
                max_depth=hyperparameters.get("max_depth", None),
                random_state=random_seed
            )
            model.fit(X, y)

        elif alg_upper == "LINEAR_REGRESSION":
            model = LinearRegression()
            model.fit(X, y)

        elif alg_upper == "RANDOM_FOREST_REGRESSOR" or alg_upper == "FORECASTING_REGRESSOR":
            model = RandomForestRegressor(
                n_estimators=int(hyperparameters.get("n_estimators", 10)),
                max_depth=hyperparameters.get("max_depth", None),
                random_state=random_seed
            )
            model.fit(X, y)

        elif alg_upper == "ISOLATION_FOREST":
            model = IsolationForest(
                n_estimators=int(hyperparameters.get("n_estimators", 10)),
                contamination=float(hyperparameters.get("contamination", 0.1)),
                random_state=random_seed
            )
            model.fit(X)

        else:
            raise ModelProviderError(f"Unsupported algorithm '{algorithm}'")

        training_meta = {
            "algorithm": alg_upper,
            "task_type": task_type,
            "samples_count": len(X),
            "features_count": X.shape[1] if len(X.shape) > 1 else 1,
            "random_seed": random_seed,
        }
        return model, training_meta
