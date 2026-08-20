# MLflow documentation

This directory contains MLflow integration for Voyage Analytics.

## Purpose

The MLflow integration is designed to track and register the trained model produced by the Google Colab ML notebook. It does NOT retrain models - it only tracks and registers the artifact.

## Architecture

```
Google Colab (ML Team)
         │
         ▼
  Model Artifact (joblib)
         │
         ▼
    MLflow (Tracking & Registration)
         │
         ▼
   Flask REST API
```

## Usage

### Starting Local MLflow

```bash
# Start MLflow tracking server locally
mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlflow/artifacts
```

### Tracking a Model from Colab

After training in Google Colab and downloading the artifacts:

```bash
python mlflow/tracking.py \
  --model-path artifacts/flight_price_pipeline.joblib \
  --metrics-path artifacts/metrics.json \
  --metadata-path artifacts/model_metadata.json \
  --run-name "model_v1_training"
```

### Using the ModelTracker Class

```python
from mlflow.tracking import ModelTracker

tracker = ModelTracker()

with tracker.start_run(run_name="my_run"):
    tracker.log_model("artifacts/flight_price_pipeline.joblib")
    tracker.log_metrics({"mae": 15.5, "rmse": 22.3, "r2": 0.92})
    tracker.log_params({"algorithm": "RandomForest", "n_estimators": 100})
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow server URI |
| `MLFLOW_EXPERIMENT_NAME` | `voyage-flight-price` | Experiment name |

## What Gets Tracked

- Model artifact (`flight_price_pipeline.joblib`)
- Model metadata (name, version, algorithm)
- Training metrics (MAE, RMSE, R²)
- Model parameters
- Feature importance (if available)

## Model Registration

Models are automatically registered in MLflow with the name `voyage_flight_price`.

View registered models:
```bash
mlflow models list
```

Get model version:
```bash
mlflow models version
```
