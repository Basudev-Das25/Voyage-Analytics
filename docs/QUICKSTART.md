# Project Setup

```bash
# Clone repository
git clone <your-repo>
cd voyage-analytics

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env
```

# Running the API

```bash
# Run with Flask development server
python -m api.app

# Or use helper script
python scripts/run_local.py
```

# Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov=api --cov-report=term-missing
```

# Docker

```bash
# Build image
docker build -f docker/Dockerfile -t voyage-analytics-api .

# Run container
docker run -p 5000:5000 \
  -e MODEL_PATH=/app/artifacts/flight_price_pipeline.joblib \
  -v $(pwd)/artifacts:/app/artifacts \
  voyage-analytics-api
```

# MLflow

```bash
# Start MLflow server (port 5001, avoids API port 5000)
docker compose -f docker/docker-compose.mlflow.yml up -d
export MLFLOW_TRACKING_URI=http://localhost:5001

# Track all models
python scripts/track_models.py
```

# Kubernetes

```bash
# Apply manifests
kubectl apply -f kubernetes/

# Check status
kubectl get pods -n voyage-analytics
kubectl get services -n voyage-analytics
```

# CI/CD

```bash
# GitHub Actions runs automatically on push
# Or manually trigger via UI
```

# Model Artifact Handoff

Place the trained model from Google Colab in `artifacts/`:

```text
artifacts/
├── flight_price_pipeline.joblib  # Required
├── metrics.json                  # Optional
├── feature_schema.json           # Optional
└── model_metadata.json           # Optional
```

# API Endpoints

- `GET /api/health` - Health check
- `GET /api/model-info` - Model metadata
- `POST /api/predict` - Predict flight price
