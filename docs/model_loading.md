# Model Loading

The model loading component handles loading and caching the flight price prediction model.

## Location

```
src/model/loader.py
```

## Key Functions

### load_model()

```python
from src.model.loader import load_model

model = load_model()
```

Loads the model from the configured path. Returns the cached model if already loaded.

### get_model()

```python
from src.model.loader import get_model

model = get_model()
```

Gets the loaded model or loads it if not already loaded.

### unload_model()

```python
from src.model.loader import ModelLoader

ModelLoader.unload_model()
```

Clears the cached model instance.

## Configuration

The model path is configurable via the `MODEL_PATH` environment variable:

```env
MODEL_PATH=artifacts/flight_price_pipeline.joblib
```

## Error Handling

The loader provides clear error messages:

- `FileNotFoundError` - Model artifact not found at configured path
- `RuntimeError` - Model loading failed for other reasons

## Caching

The model is cached in memory after the first load to avoid repeated file I/O. This is important for API performance.

## Testing

Tests are in `tests/test_model_loader.py`:

```bash
pytest tests/test_model_loader.py
```

## Integration

The model loader is used by the prediction service:

```python
from src.model.loader import get_model

model = get_model()
prediction = model.predict([input_data])
```
