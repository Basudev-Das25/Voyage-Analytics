# Voyage Analytics: MLOps Production Layer

Voyage Analytics integrates MLOps in travel by productionizing ML systems for flight price prediction.

## Overview

This repository contains the production/MLOps layer for Voyage Analytics. It consumes trained model artifacts from the ML team and exposes them via a REST API for integration with downstream systems (including the Streamlit/recommendation component).

### Architecture

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

## Division of Responsibilities

| Component | Owner |
|-----------|-------|
| Flight price regression | ML Team |
| Data preprocessing | ML Team |
| Feature engineering | ML Team |
| Model comparison/evaluation | ML Team |
| Model training (Colab) | ML Team |
| **Model artifact integration** | **MLOps Team** |
| **Flask REST API** | **MLOps Team** |
| **Automated testing** | **MLOps Team** |
| **Docker** | **MLOps Team** |
| **Kubernetes** | **MLOps Team** |
| **CI/CD** | **MLOps Team** |

## Model Artifact Handoff

The ML team will produce artifacts in `artifacts/`:

```text
artifacts/
├── flight_price_pipeline.joblib    # Required
├── metrics.json                     # Optional
├── feature_schema.json              # Optional
└── model_metadata.json              # Optional
```

**Do NOT replace or regenerate this artifact.** The production code loads it as-is.

## Quick Start

### Prerequisites

- Python 3.9+
- pip
- Docker (optional)
- kubectl (optional)

### Local Setup

```bash
# Clone this repository
git clone <your-repo>
cd voyage-analytics

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env
```

Edit `.env` to set your model path (default points to the dummy model):

```env
MODEL_PATH=artifacts/flight_price_pipeline.joblib
MLFLOW_TRACKING_URI=http://localhost:5000
API_HOST=0.0.0.0
API_PORT=5000
```

### Running the API

```bash
# Start Flask development server
python -m api.app

# Or use the helper script
python scripts/run_local.py
```

### Running Tests

```bash
pytest
```

### Docker

```bash
# Build image
docker build -f docker/Dockerfile -t voyage-analytics-api .

# Run container (with model mounted)
docker run -p 5000:5000 \
  -e MODEL_PATH=/app/artifacts/flight_price_pipeline.joblib \
  -v $(pwd)/artifacts:/app/artifacts \
  voyage-analytics-api
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /model-info | Model metadata |
| POST | /predict | Predict flight price |

## Project Structure

```
voyage-analytics/
├── artifacts/           # Model artifacts (from ML team)
├── config/              # Configuration
├── src/                 # Application source
│   ├── model/           # Model loading
│   ├── schemas/         # Input/Output schemas
│   └── services/        # Business logic
├── api/                 # Flask API
├── tests/               # Test suite
├── scripts/             # Utility scripts
├── mlflow/              # MLflow integration
├── docker/              # Docker configuration
├── kubernetes/          # Kubernetes manifests
├── airflow/             # Orchestration (template)
├── docs/                # Documentation
└── .github/workflows/   # CI/CD pipeline
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `artifacts/flight_price_pipeline.joblib` | Path to model artifact |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow tracking URI |
| `API_HOST` | `0.0.0.0` | API host |
| `API_PORT` | `5000` | API port |

## Next Steps

1. Replace `tests/fixtures/dummy_model.joblib` with the real `flight_price_pipeline.joblib` from Google Colab
2. Configure MLflow for model registration
3. Deploy to Kubernetes for production

## License

Academic project - Voyage Analytics Capstone
