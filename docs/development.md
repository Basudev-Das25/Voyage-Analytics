# Development Guide

## Setup

### Prerequisites

- Python 3.9+
- pip
- Git

### Installation

```bash
# Clone the repository
git clone <your-repo>
cd voyage-analytics

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# (default values work for development)
```

## Running the Application

### Start Development Server

```bash
# Using the helper script (creates dummy model if needed)
python scripts/run_local.py

# Or directly
python -m api.app
```

The API will be available at `http://localhost:5000`.

### Available Endpoints

- `GET http://localhost:5000/api/health` - Health check
- `GET http://localhost:5000/api/model-info` - Model metadata
- `POST http://localhost:5000/api/predict` - Predict flight price

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_health.py
pytest tests/test_prediction.py
pytest tests/test_model_loader.py
```

### Run with Coverage

```bash
pytest --cov=src --cov=api --cov-report=term-missing
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test

```bash
pytest tests/test_health.py::test_health_check
```

### Test with Debug

```bash
pytest -s  # Disable output capturing
```

## Project Structure

```
voyage-analytics/
├── src/              # Application source code
│   ├── model/        # Model loading utilities
│   ├── schemas/      # Input/Output schemas
│   └── services/     # Business logic
├── api/              # Flask API
│   ├── app.py        # Flask application factory
│   └── routes.py     # API routes
├── tests/            # Test suite
│   ├── fixtures/     # Test fixtures (dummy model)
│   ├── test_health.py
│   ├── test_prediction.py
│   └── test_model_loader.py
├── artifacts/        # Model artifacts (from ML team)
├── config/           # Configuration
├── scripts/          # Utility scripts
├── mlflow_tracking/  # MLflow integration (wraps official mlflow lib)
├── docker/           # Docker configuration
└── kubernetes/       # Kubernetes manifests
```

## Development Commands

### Create Dummy Model

```bash
# Automatically creates if needed
python scripts/run_local.py --create-dummy

# Or manually
python tests/fixtures/dummy_model.py
```

### Validate Model Artifact

```bash
python scripts/validate_artifact.py
```

### Lint Code

```bash
# Flake8
flake8 src/ api/

# Black (formatting)
black src/ api/ tests/ scripts/

# Mypy (type checking)
mypy src/ api/
```

### Check Code Quality

```bash
# Run all checks
flake8 src/ api/
black --check src/ api/ tests/ scripts/
mypy src/ api/
```

## Adding New Features

### Add New API Endpoint

1. Define input/output schema in `src/schemas/prediction.py`
2. Add service logic in `src/services/`
3. Create route in `api/routes.py`
4. Add test in `tests/`

### Modify Model Loading

1. Update `src/model/loader.py`
2. Update tests in `tests/test_model_loader.py`
3. Test with dummy model first

### Add New Configuration

1. Update `config/settings.py`
2. Add to `.env.example`
3. Update tests if needed

## MLflow Integration

### Start MLflow Server

```bash
# Install the MLflow tracking dependency
pip install -r requirements-dev.txt

# Option A: bundled Docker server on port 5001 (avoids API port 5000)
docker compose -f docker/docker-compose.mlflow.yml up -d
export MLFLOW_TRACKING_URI=http://localhost:5001

# Option B: local server directly
mlflow server --host 0.0.0.0 --port 5001
export MLFLOW_TRACKING_URI=http://localhost:5001
```

### Track Model

```bash
python mlflow_tracking/tracking.py \
  --model-path artifacts/flight_price_pipeline.joblib \
  --metrics-path artifacts/metrics.json \
  --metadata-path artifacts/model_metadata.json
```

## Common Tasks

### Replace Dummy Model with Real Model

1. Train model in Google Colab
2. Download `flight_price_pipeline.joblib`
3. Copy to `artifacts/` directory
4. Restart Flask application

### Debug Model Loading

```python
import joblib
from src.model.loader import load_model

try:
    model = load_model()
    print(f"Model loaded: {model}")
except Exception as e:
    print(f"Error: {e}")
```

### Check Environment Variables

```bash
python -c "from config.settings import settings; print(settings.model_path)"
```
