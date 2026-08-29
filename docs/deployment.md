# Deployment Guide

## Prerequisites

- Docker installed and running
- Kubernetes cluster (optional, for K8s deployment)
- Python 3.9+ (for local development)

## Local Deployment

### 1. Clone and Setup

```bash
git clone <your-repo>
cd voyage-analytics
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Copy Environment Template

```bash
cp .env.example .env
```

### 4. Configure Environment

Edit `.env`:

```env
MODEL_PATH=artifacts/flight_price_pipeline.joblib
MLFLOW_TRACKING_URI=http://localhost:5000
API_HOST=0.0.0.0
API_PORT=5000
```

### 5. Create Dummy Model (Development Only)

```bash
python scripts/run_local.py --create-dummy
```

### 6. Run the API

```bash
python -m api.app
```

Or:

```bash
python scripts/run_local.py
```

The API will be available at `http://localhost:5000`.

## Docker Deployment

### Build Image

```bash
docker build -f docker/Dockerfile -t voyage-analytics-api .
```

### Run Container

```bash
docker run -p 5000:5000 \
  -e MODEL_PATH=/app/artifacts/flight_price_pipeline.joblib \
  -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 \
  -v $(pwd)/artifacts:/app/artifacts \
  voyage-analytics-api
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "5000:5000"
    environment:
      - MODEL_PATH=/app/artifacts/flight_price_pipeline.joblib
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    volumes:
      - ./artifacts:/app/artifacts
    depends_on:
      - mlflow

  mlflow:
    image: mlflow/mlflow:latest
    ports:
      - "5001:5000"
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:///mlflow.db
      --default-artifact-root ./mlflow/artifacts
```

Run:

```bash
docker-compose up
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster
- `kubectl` configured
- Docker registry access

### Build and Push Docker Image

```bash
docker build -f docker/Dockerfile -t voyage-analytics-api:latest .
docker tag voyage-analytics-api:latest <your-dockerhub>/<repo>:latest
docker push <your-dockerhub>/<repo>:latest
```

### Update Kubernetes Config

Edit `kubernetes/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: voyage-analytics-config
  namespace: voyage-analytics
data:
  MODEL_PATH: "artifacts/flight_price_pipeline.joblib"
  MLFLOW_TRACKING_URI: "http://mlflow-service:5000"
  MLFLOW_EXPERIMENT_NAME: "voyage-flight-price"
  API_HOST: "0.0.0.0"
  API_PORT: "5000"
```

### Deploy

```bash
kubectl apply -f kubernetes/
```

### Verify

```bash
kubectl get pods -n voyage-analytics
kubectl get services -n voyage-analytics
kubectl logs -n voyage-analytics -l app=voyage-analytics-api
```

## Troubleshooting

### Model Not Found

```text
FileNotFoundError: Model artifact not found at: artifacts/flight_price_pipeline.joblib
```

**Solution:** Ensure the model artifact exists in `artifacts/` directory or set `MODEL_PATH` correctly.

### Port Already in Use

```text
OSError: [Errno 98] Address already in use
```

**Solution:** Change `API_PORT` in `.env` or kill existing process.

### Container Won't Start

```bash
# Check logs
docker logs <container-id>
kubectl logs -n voyage-analytics <pod-name>
```

### Health Check Fails

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# For K8s
kubectl exec -n voyage-analytics <pod-name> -- curl localhost:5000/api/health
```

## Scaling

### Docker

```bash
# Not directly supported - use Docker Compose or K8s
```

### Kubernetes

```bash
# Scale to 5 replicas
kubectl scale deployment voyage-analytics-api -n voyage-analytics --replicas=5

# Check replicas
kubectl get deployments -n voyage-analytics
```
