# Voyage Analytics: MLOps Production Layer

Voyage Analytics integrates MLOps in travel by productionizing ML systems for
flight price prediction, gender classification, and hotel recommendation.

## Overview

This repository contains the production/MLOps layer for Voyage Analytics. It
consumes model artifacts built from the ML team's Colab notebook and exposes
them via a Flask REST API for integration with downstream systems (including
the Streamlit dashboard).

### Models

| Model | Source dataset | Artifact | Task | Endpoint |
|-------|----------------|----------|------|----------|
| Flight price | `flights.csv` (+ users/hotels) | `artifacts/flight_price_pipeline.joblib` | Regression (XGBoost) | `POST /api/predict` |
| Gender | `users.csv` | `artifacts/gender_model.joblib` | Classification (RandomForest) | `POST /api/gender/predict` |
| Hotel recommendation | `hotels.csv` + `users.csv` | `artifacts/hotel_catalog.json` | Content-based filtering | `POST /api/recommend/recommendations` |

### Architecture

```
Google Colab (ML Team)
         │
         ▼
  Model Artifacts (joblib / json)
         │
         ▼
    MLflow (Tracking / Registry)
         │
         ▼
   Flask REST API  ◄── Streamlit Dashboard
         │
    ┌────┴────┐
    ▼         ▼
  Docker   Kubernetes
```

## Division of Responsibilities

| Component | Owner |
|-----------|-------|
| Flight price regression / gender / recommendation models | ML Team |
| Data preprocessing & feature engineering | ML Team |
| Model comparison/evaluation | ML Team |
| Model training (Colab) | ML Team |
| **Model artifact integration** | **MLOps Team** |
| **Flask REST API** | **MLOps Team** |
| **Automated testing** | **MLOps Team** |
| **Streamlit dashboard** | **MLOps Team** |
| **Docker** | **MLOps Team** |
| **Kubernetes** | **MLOps Team** |
| **CI/CD** | **MLOps Team** |

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### Local Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Running the API

```bash
python -m api.app                 # or: python scripts/run_local.py
```

The API exposes the following endpoints (see `docs/api.md`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/model-info` | Flight-price model metadata |
| POST | `/api/predict` | Predict flight price |
| GET | `/api/gender/health` | Gender endpoint health |
| POST | `/api/gender/predict` | Classify user gender |
| GET | `/api/recommend/health` | Recommendation endpoint health |
| GET | `/api/recommend/places` | List destination cities |
| POST | `/api/recommend/recommendations` | Get hotel recommendations |

### Running Tests

```bash
pytest
```

### Streamlit Dashboard

```bash
# With the API running, launch the dashboard:
streamlit run dashboard/app.py
```

The dashboard provides an interactive flight-price predictor, gender
classifier, hotel recommender, and data insights.

## Building the Artifacts

The gender model and recommendation catalog are tracked in the repo. The raw
datasets (`flights.csv`, `hotels.csv`, `users.csv`) live in `artifacts/data/`.
To regenerate the artifacts from these datasets:

```bash
# Train the gender classification model from users.csv
python scripts/train_gender_model.py --data-path artifacts/data/users.csv

# Build the hotel recommendation catalog from hotels.csv + users.csv
python scripts/build_recommendation_catalog.py \
    --hotels artifacts/data/hotels.csv \
    --users artifacts/data/users.csv
```

The flight-price model (`artifacts/flight_price_pipeline.joblib`) is supplied
by the ML team from the Colab notebook and is git-ignored (large binary). Place
it at `MODEL_PATH` (default `artifacts/flight_price_pipeline.joblib`).

## MLflow Tracking

Track, log and register all models with MLflow. Start the bundled tracking
server (port 5001) with Docker:

```bash
docker compose -f docker/docker-compose.mlflow.yml up -d
export MLFLOW_TRACKING_URI=http://localhost:5001
```

Install the tracking dependency and run:

```bash
pip install -r requirements-dev.txt
python scripts/track_models.py
```

See `mlflow_tracking/README.md` for details.

## Docker

```bash
docker build -f docker/Dockerfile -t voyage-analytics-api .
docker run -p 5000:5000 voyage-analytics-api
```

## Kubernetes

```bash
kubectl apply -f kubernetes/
```

See `kubernetes/README.md` for details.

## Project Structure

```
voyage-analytics/
├── api/                 # Flask blueprints (predict, gender, recommend)
├── artifacts/           # Model artifacts + recommendation catalog
├── config/              # Configuration
├── src/
│   ├── features/        # Shared feature engineering
│   ├── model/           # Model loaders
│   ├── schemas/         # Input/Output schemas
│   └── services/        # Business logic
├── scripts/             # Training / catalog / tracking / utility scripts
├── dashboard/           # Streamlit web app
├── tests/               # Test suite
├── mlflow_tracking/     # MLflow integration (wraps official mlflow lib)
├── docker/              # Docker configuration
├── kubernetes/          # Kubernetes manifests
├── airflow/             # Orchestration (template)
├── docs/                # Documentation
└── .github/workflows/   # CI/CD pipeline
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `artifacts/flight_price_pipeline.joblib` | Flight-price model artifact |
| `GENDER_MODEL_PATH` | `artifacts/gender_model.joblib` | Gender model artifact |
| `HOTELS_CATALOG_PATH` | `artifacts/hotel_catalog.json` | Recommendation catalog |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow tracking URI |
| `API_HOST` | `0.0.0.0` | API host |
| `API_PORT` | `5000` | API port |

## License

Academic project - Voyage Analytics Capstone
