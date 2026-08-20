# Architecture

## High-Level Architecture

```
Google Colab (ML Team)
         │
         ▼
  Model Artifact (joblib)
         │
         ▼
    MLflow (Tracking)
         │
         ▼
   Flask REST API
         │
    ┌────┴────┐
    ▼         ▼
 Docker   Kubernetes
```

## Component Breakdown

### 1. ML Team (Google Colab)

The ML team trains the flight price prediction model:

- Data preprocessing
- Feature engineering
- Model training and comparison
- Model evaluation
- Artifact generation (`flight_price_pipeline.joblib`)

### 2. Model Artifact

The trained model is exported as a joblib file containing the complete pipeline:

```text
artifacts/
└── flight_price_pipeline.joblib
```

### 3. MLflow (Tracking)

MLflow tracks model metadata, metrics, and parameters:

- Model registration
- Experiment tracking
- Metrics logging
- Parameter tracking

### 4. Flask REST API

The production layer exposes model inference via REST:

- `/health` - Health check
- `/model-info` - Model metadata
- `/predict` - Price prediction

### 5. Docker

The API is containerized for portable deployment:

- Lightweight Python 3.9 slim image
- Production-grade configuration
- Environment-based configuration

### 6. Kubernetes

The container is deployed to Kubernetes:

- Horizontal scaling (multiple replicas)
- Health monitoring (liveness/readiness probes)
- Service discovery

## Data Flow

```
[Colab Notebook]
    │
    ▼
[Export Model Artifact]
    │
    ▼
[Copy to artifacts/]
    │
    ▼
[Flask App Loads Model]
    │
    ▼
[API Receives Request]
    │
    ▼
[Model Predicts Price]
    │
    ▼
[Return JSON Response]
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Model Training | scikit-learn, Google Colab |
| Model Storage | joblib |
| Tracking | MLflow |
| API | Flask, Pydantic |
| Container | Docker |
| Orchestration | Kubernetes |

## Configuration Management

Configuration is externalized via environment variables:

| Variable | Purpose |
|----------|---------|
| `MODEL_PATH` | Path to model artifact |
| `MLFLOW_TRACKING_URI` | MLflow server URI |
| `MLFLOW_EXPERIMENT_NAME` | Experiment name |
| `API_HOST` | API bind address |
| `API_PORT` | API port |

## Testing Strategy

- Unit tests for model loader
- Integration tests for API endpoints
- Dummy model for development (no real artifact needed)
- Coverage: 80%+ target
