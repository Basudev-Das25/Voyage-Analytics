"""MLflow tracking integration for Voyage Analytics.

This module provides utilities for tracking and registering the trained model
produced by the Google Colab ML notebook. It does NOT retrain models.

The purpose is to track model metadata, metrics, and register the model artifact
for deployment in the production pipeline.
"""

import os
import json
import logging
from typing import Optional, Dict, Any

import mlflow
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient

from config.settings import settings

logger = logging.getLogger(__name__)


class ModelTracker:
    """Manages model tracking and registration with MLflow."""

    def __init__(self):
        self.tracking_uri = settings.mlflow_tracking_uri
        self.experiment_name = settings.mlflow_experiment_name
        self.client = MlflowClient(self.tracking_uri)

        # Set experiment
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)

    def start_run(self, run_name: str = "production_run") -> mlflow.ActiveRun:
        """
        Start a new MLflow run for tracking.

        Args:
            run_name: Name for this run

        Returns:
            Active MLflow run context
        """
        return mlflow.start_run(run_name=run_name)

    def log_model(
        self,
        model_path: str,
        artifact_path: str = "flight_price_pipeline",
        registered: bool = True,
    ) -> Optional[str]:
        """
        Log and optionally register the model.

        Args:
            model_path: Path to the model artifact (joblib file)
            artifact_path: Path where model will be stored in MLflow
            registered: Whether to register the model

        Returns:
            Model URI if registered, None otherwise
        """
        # Log the model
        model_info = mlflow.log_model(
            model_uri=model_path,
            artifact_path=artifact_path,
            conda_env=self._get_conda_env(),
        )

        logger.info(f"Model logged: {model_info.model_uri}")

        if registered:
            # Register the model
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/{artifact_path}"
            registered_model = mlflow.register_model(
                model_uri=model_uri,
                name="voyage_flight_price",
            )

            logger.info(f"Model registered: {registered_model.name} v{registered_model.version}")
            return model_uri

        return None

    def log_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Log model metrics.

        Args:
            metrics: Dictionary of metric name -> value
        """
        for name, value in metrics.items():
            mlflow.log_metric(name, value)
        logger.info(f"Logged {len(metrics)} metrics")

    def log_params(self, params: Dict[str, Any]) -> None:
        """
        Log model parameters.

        Args:
            params: Dictionary of parameter name -> value
        """
        for name, value in params.items():
            mlflow.log_param(name, value)
        logger.info(f"Logged {len(params)} parameters")

    def log_artifact(self, local_path: str, artifact_path: str = None) -> None:
        """
        Log an artifact (file) to MLflow.

        Args:
            local_path: Path to the local file
            artifact_path: Optional subdirectory in the artifact URI
        """
        mlflow.log_artifact(local_path, artifact_path)
        logger.info(f"Logged artifact: {local_path}")

    def log_model_metadata(
        self,
        model_path: str,
        metadata_path: str = None,
    ) -> None:
        """
        Log model metadata to MLflow.

        Args:
            model_path: Path to the model artifact
            metadata_path: Optional path to metadata JSON file
        """
        # Load metadata if file exists
        metadata = {
            "model_type": "flight_price_regression",
            "framework": "scikit-learn",
        }

        if metadata_path and os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    file_metadata = json.load(f)
                    metadata.update(file_metadata)
            except Exception:
                pass

        # Log as JSON artifact
        metadata_json = json.dumps(metadata, indent=2)
        with open("model_metadata.json", "w") as f:
            f.write(metadata_json)
        self.log_artifact("model_metadata.json", "metadata")

        # Log each field as a param
        for key, value in metadata.items():
            mlflow.log_param(key, str(value))

        logger.info("Logged model metadata")

    def _get_conda_env(self) -> Dict[str, Any]:
        """Get conda environment specification for model deployment."""
        return {
            "name": "voyage-analytics-env",
            "channels": ["conda-forge", "defaults"],
            "dependencies": [
                "python=3.9",
                "pip",
                {
                    "pip": [
                        "flask==3.0.0",
                        "joblib==1.3.2",
                        "pydantic==2.5.0",
                        "numpy>=1.24.0",
                        "pandas>=2.0.0",
                    ],
                },
            ],
        }


def track_model_from_colab(
    model_path: str,
    metrics_path: str = None,
    metadata_path: str = None,
    run_name: str = "colab_training_run",
) -> Dict[str, str]:
    """
    Track a model trained in Google Colab.

    This function is designed to be called after training the model in Colab
    and downloading the artifacts to this project.

    Args:
        model_path: Path to flight_price_pipeline.joblib
        metrics_path: Optional path to metrics.json
        metadata_path: Optional path to model_metadata.json
        run_name: Name for this MLflow run

    Returns:
        Dictionary with run_id and model_uri
    """
    tracker = ModelTracker()

    with tracker.start_run(run_name=run_name):
        # Log model
        model_uri = tracker.log_model(model_path)

        # Log metrics if available
        if metrics_path and os.path.exists(metrics_path):
            try:
                with open(metrics_path, "r") as f:
                    metrics = json.load(f)
                tracker.log_metrics(metrics)
            except Exception:
                logger.warning("Could not load metrics file")

        # Log metadata
        tracker.log_model_metadata(model_path, metadata_path)

        # Return run info
        run_id = mlflow.active_run().info.run_id

        return {
            "run_id": run_id,
            "model_uri": model_uri,
            "experiment_name": tracker.experiment_name,
        }


def get_latest_model_version(model_name: str = "voyage_flight_price") -> Optional[int]:
    """
    Get the latest version of a registered model.

    Args:
        model_name: Name of the registered model

    Returns:
        Version number or None if not found
    """
    client = MlflowClient()

    try:
        model_versions = client.search_model_versions(f"name='{model_name}'")

        if not model_versions:
            return None

        # Get latest version (highest version number)
        versions = [int(v.version) for v in model_versions]
        return max(versions)

    except Exception:
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Track a trained model with MLflow"
    )
    parser.add_argument(
        "--model-path",
        default="artifacts/flight_price_pipeline.joblib",
        help="Path to trained model artifact",
    )
    parser.add_argument(
        "--metrics-path",
        default="artifacts/metrics.json",
        help="Path to metrics JSON file",
    )
    parser.add_argument(
        "--metadata-path",
        default="artifacts/model_metadata.json",
        help="Path to model metadata JSON file",
    )
    parser.add_argument(
        "--run-name",
        default="colab_training_run",
        help="MLflow run name",
    )
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="Do not register the model",
    )

    args = parser.parse_args()

    print("Starting MLflow tracking...")
    print(f"  Model: {args.model_path}")

    tracker = ModelTracker()
    print(f"  Experiment: {tracker.experiment_name}")
    print(f"  Tracking URI: {tracker.tracking_uri}")

    with tracker.start_run(run_name=args.run_name):
        tracker.log_model(args.model_path, registered=not args.no_register)

        if os.path.exists(args.metrics_path):
            tracker.log_artifact(args.metrics_path, "artifacts")

        if os.path.exists(args.metadata_path):
            tracker.log_artifact(args.metadata_path, "artifacts")

        print(f"  Run ID: {mlflow.active_run().info.run_id}")
        print("✓ Tracking complete")
