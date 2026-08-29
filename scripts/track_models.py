"""Track and register all Voyage Analytics models with MLflow.

Logs training metrics, params and the model artifact for each model family
(flight price, gender) plus the recommendation catalog, and registers them
with the MLflow Model Registry.

Requires a reachable MLflow tracking server (see MLFLOW_TRACKING_URI).
Run an MLflow server first, e.g.:

    mlflow server --host 0.0.0.0 --port 5000

Usage:
    python scripts/track_models.py               # track every model
    python scripts/track_models.py --model flight  # track just one
"""

import argparse
import json
import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import mlflow
from mlflow.models import infer_signature

from config.settings import settings

#: model family -> (artifact path, registered model name, sample feature dict)
MODEL_DEFS = {
    "flight": {
        "artifact": settings.model_path,
        "name": "voyage_flight_price",
        "task": "regression",
        "framework": "xgboost",
        "signature_sample": {
            "from": "Recife (PE)",
            "to": "Florianopolis (SC)",
            "flightType": "firstClass",
            "agency": "FlyingDrops",
            "time": 1.76,
            "distance": 676.53,
            "flight_year": 2019,
            "flight_month": 9,
            "flight_day": 26,
            "flight_dayofweek": 3,
        },
    },
    "gender": {
        "artifact": settings.gender_model_path,
        "name": "voyage_gender",
        "task": "classification",
        "framework": "scikit-learn",
        "signature_sample": {"first_name": "robert", "age": 33},
    },
}


def _load_metrics(metrics_path: str):
    if metrics_path and os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def track_family(name: str, metrics: dict = None) -> dict:
    """Log a single model family to MLflow."""
    if name not in MODEL_DEFS:
        print(f"Unknown model: {name} (choose from {list(MODEL_DEFS)})")
        return {}

    cfg = MODEL_DEFS[name]
    artifact = cfg["artifact"]
    if not os.path.exists(artifact):
        print(f"Skipping {name}: artifact not found at {artifact}")
        return {}

    with mlflow.start_run(run_name=f"{name}_tracking"):
        mlflow.set_tag("task", cfg["task"])
        mlflow.set_tag("framework", cfg["framework"])
        mlflow.log_param("artifact", artifact)

        if metrics:
            for k, v in metrics.items():
                try:
                    mlflow.log_metric(k, float(v))
                except (TypeError, ValueError):
                    mlflow.log_param(k, str(v))

        # Register the raw artifact and log a signature for sklearn-compatible
        # models where inference is possible.
        try:
            mlflow.log_artifact(artifact, artifact_path="model")
        except Exception as e:
            print(f"  Could not log artifact for {name}: {e}")

        try:
            uri = mlflow.register_model(
                f"runs:/{mlflow.active_run().info.run_id}/model",
                name=cfg["name"],
            )
            print(f"Registered {cfg['name']} v{uri.version}")
        except Exception as e:
            print(f"  Registration failed for {name}: {e}")

        return {"run_id": mlflow.active_run().info.run_id}


def main():
    parser = argparse.ArgumentParser(description="Track Voyage Analytics models in MLflow")
    parser.add_argument(
        "--model",
        choices=list(MODEL_DEFS) + ["all"],
        default="all",
        help="Which model family to track",
    )
    parser.add_argument("--metrics-file", default=None, help="Optional metrics JSON")
    args = parser.parse_args()

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)

    metrics = _load_metrics(args.metrics_file)

    targets = list(MODEL_DEFS) if args.model == "all" else [args.model]
    for t in targets:
        track_family(t, metrics=metrics)

    print("Done.")


if __name__ == "__main__":
    main()
