# Input Schemas

This module defines Pydantic schemas for input validation and output formatting.

## Location

```
src/schemas/prediction.py
```

## Input Schema: FlightPredictionInput

Defines the expected structure for prediction requests.

### Fields

| Field | Type | Validation |
|-------|------|------------|
| flight_duration | float | Must be > 0 |
| distance | float | Must be > 0 |
| airline | string | Min 1 character |
| departure_hour | int | 0-23 |
| day_of_week | int | 0-6 |
| is_weekend | bool | Optional (default: false) |
| is_holiday | bool | Optional (default: false) |
| days_until_departure | int | Must be > 0 |
| class_type | string | One of: economy, business, first |
| origin_airport | string | 3-4 characters |
| destination_airport | string | 3-4 characters |

### Example

```json
{
  "flight_duration": 5.5,
  "distance": 4500.0,
  "airline": "UA",
  "departure_hour": 14,
  "day_of_week": 2,
  "is_weekend": false,
  "is_holiday": false,
  "days_until_departure": 21,
  "class_type": "economy",
  "origin_airport": "JFK",
  "destination_airport": "LAX"
}
```

## Output Schemas

### FlightPredictionOutput

Response format for predictions.

```json
{
  "predicted_price": 450.75,
  "model_version": "1.0",
  "model_name": "flight_price_regression"
}
```

### HealthCheck

Response format for health endpoint.

```json
{
  "status": "healthy"
}
```

### ModelInfo

Response format for model info endpoint.

```json
{
  "model_name": "flight_price_regression",
  "model_version": "1.0",
  "status": "loaded"
}
```

### ErrorResponse

Standardized error response format.

```json
{
  "error": "Validation failed",
  "field": "departure_hour",
  "code": "invalid_value"
}
```

## Usage

### In API Routes

```python
from src.schemas.prediction import FlightPredictionInput

# Parse and validate request data
input_data = FlightPredictionInput(**request_data)

# Convert to dict for model prediction
input_dict = input_data.model_dump()
```

### In Tests

```python
from src.schemas.prediction import FlightPredictionInput

# Create valid test data
valid_input = FlightPredictionInput(
    flight_duration=5.5,
    distance=4500.0,
    airline="UA",
    departure_hour=14,
    day_of_week=2,
    is_weekend=False,
    is_holiday=False,
    days_until_departure=21,
    class_type="economy",
    origin_airport="JFK",
    destination_airport="LAX"
)
```

## Error Handling

Invalid input raises Pydantic validation errors:

```python
try:
    input_data = FlightPredictionInput(**invalid_data)
except ValidationError as e:
    # Return HTTP 400 with validation errors
    return error_response(str(e))
```

## Extensibility

The schema is designed to be updated when the real model artifact provides the actual feature names. Simply update the field definitions in `FlightPredictionInput`.
