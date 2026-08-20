# API Documentation

## Endpoints

### GET /api/health

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200` - API is healthy
- `503` - Model loading failed

---

### GET /api/model-info

Returns information about the loaded model.

**Response:**
```json
{
  "model_name": "flight_price_regression",
  "model_version": "1.0",
  "status": "loaded"
}
```

**Status Codes:**
- `200` - Success
- `503` - Model not available

---

### POST /api/predict

Predicts flight price based on input features.

**Request Body:**
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

**Response (Success):**
```json
{
  "predicted_price": 450.75,
  "model_version": "1.0",
  "model_name": "flight_price_regression"
}
```

**Response (Error):**
```json
{
  "error": "Invalid input data",
  "field": "departure_hour",
  "code": "validation_failed"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid input (missing field, invalid value, malformed JSON)
- `500` - Model prediction failed
- `503` - Model not available

---

## Request Schema

### FlightPredictionInput

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| flight_duration | float | Yes | Duration in hours (must be > 0) |
| distance | float | Yes | Distance in kilometers (must be > 0) |
| airline | string | Yes | Airline code (min 1 char) |
| departure_hour | int | Yes | Hour (0-23) |
| day_of_week | int | Yes | Day (0-6) |
| is_weekend | bool | No | Weekend flag (default: false) |
| is_holiday | bool | No | Holiday flag (default: false) |
| days_until_departure | int | Yes | Days until departure (must be > 0) |
| class_type | string | Yes | One of: economy, business, first |
| origin_airport | string | Yes | Origin airport code (3-4 chars) |
| destination_airport | string | Yes | Destination airport code (3-4 chars) |

---

## Error Responses

### 400 Bad Request - Validation Error

```json
{
  "error": "Invalid input data",
  "field": "departure_hour",
  "code": "validation_failed"
}
```

### 400 Bad Request - Invalid JSON

```json
{
  "error": "Invalid JSON payload",
  "code": "invalid_json"
}
```

### 503 Service Unavailable - Model Not Found

```json
{
  "error": "Model artifact not found",
  "code": "model_unavailable"
}
```

### 500 Internal Server Error

```json
{
  "error": "Prediction failed",
  "code": "prediction_failed"
}
```

---

## Example cURL Commands

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Get Model Info
```bash
curl http://localhost:5000/api/model-info
```

### Make Prediction
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```
