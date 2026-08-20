# Configuration

This project uses environment variables for configuration. All configuration is managed by `config/settings.py`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `artifacts/flight_price_pipeline.joblib` | Path to the model artifact |
| `MODEL_METADATA_PATH` | `artifacts/model_metadata.json` | Path to model metadata JSON |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow tracking server URI |
| `MLFLOW_EXPERIMENT_NAME` | `voyage-flight-price` | MLflow experiment name |
| `API_HOST` | `0.0.0.0` | API bind address |
| `API_PORT` | `5000` | API port |
| `TESTING` | `false` | Enable testing mode |

## Configuration File

The `config/settings.py` module loads environment variables at startup:

```python
from config.settings import settings

# Access configuration
print(settings.model_path)
print(settings.api_port)
print(settings.mlflow_tracking_uri)
```

## Development vs Production

### Development (.env)
```env
MODEL_PATH=artifacts/flight_price_pipeline.joblib
MLFLOW_TRACKING_URI=http://localhost:5000
API_HOST=0.0.0.0
API_PORT=5000
```

### Production (Kubernetes ConfigMap)
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: voyage-analytics-config
data:
  MODEL_PATH: "artifacts/flight_price_pipeline.joblib"
  MLFLOW_TRACKING_URI: "http://mlflow-service:5000"
  API_HOST: "0.0.0.0"
  API_PORT: "5000"
```

## Runtime Configuration

The configuration is loaded once at module import. To reload after environment changes:

```python
import importlib
from config import settings
importlib.reload(settings)
```

## Validation

Configuration is validated at startup:

- `MODEL_PATH` - Must be a valid path (file existence checked on load)
- `API_PORT` - Must be a valid port number (1-65535)
- `MLFLOW_TRACKING_URI` - Should be a valid URL

## Adding New Configuration

1. Add variable to `.env.example`
2. Add property to `config/settings.py`
3. Use in application code via `settings.VARIABLE_NAME`
