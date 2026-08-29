# API Documentation

The Voyage Analytics API is a Flask application exposing three ML services:
**flight price prediction** (regression), **gender classification**, and
**hotel recommendation** (content-based). All endpoints return JSON.

## General Endpoints

### GET /api/health

Returns the health status of the API.

**Response:**
```json
{ "status": "healthy" }
```

**Status Codes:** `200`, `503` (if model loading failed).

### GET /api/model-info

Returns metadata about the loaded flight-price model.

**Response:**
```json
{
  "model_name": "flight_price_regression",
  "model_version": "1.0",
  "status": "loaded"
}
```

---

## Flight Price Prediction

### POST /api/predict

Predicts flight price based on route, class, agency and date-derived features.

**Request Body:**
```json
{
  "from": "Recife (PE)",
  "to": "Florianopolis (SC)",
  "flightType": "firstClass",
  "agency": "FlyingDrops",
  "time": 1.76,
  "distance": 676.53,
  "flight_year": 2019,
  "flight_month": 9,
  "flight_day": 26,
  "flight_dayofweek": 3
}
```

**Fields**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| from | string | Yes | Origin city |
| to | string | Yes | Destination city |
| flightType | string | Yes | `firstClass`, `economic`, or `premium` |
| agency | string | Yes | Travel agency |
| time | number | Yes | Flight duration (hours, > 0) |
| distance | number | Yes | Distance (km, > 0) |
| flight_year | int | Yes | Year |
| flight_month | int | Yes | Month (1-12) |
| flight_day | int | Yes | Day (1-31) |
| flight_dayofweek | int | Yes | Day of week (0=Monday .. 6=Sunday) |

**Response (Success):**
```json
{
  "predicted_price": 451.2988,
  "model_version": "1.0",
  "model_name": "flight_price_regression"
}
```

**Status Codes:** `200`, `400` (validation), `500` (prediction failed), `503` (model unavailable).

---

## Gender Classification

### GET /api/gender/health

**Response:** `{ "status": "healthy" }`

### POST /api/gender/predict

Classifies a user's gender from their profile.

**Request Body:**
```json
{
  "user name": "Robert Braun",
  "age": 33,
  "company": "4You"
}
```

**Response (Success):**
```json
{
  "gender": "male",
  "probability": 0.995,
  "model_version": "1.0"
}
```

`gender` is one of `male`, `female`, `none`.

**Status Codes:** `200`, `400` (validation), `503` (model unavailable), `500` (prediction failed).

---

## Hotel Recommendation

### GET /api/recommend/health

**Response:** `{ "status": "healthy" }`

### GET /api/recommend/places

Lists all destination cities with hotels in the catalog.

**Response:**
```json
{
  "places": ["Rio de Janeiro (RJ)", "Sao Paulo (SP)", "..."],
  "total": 9
}
```

### POST /api/recommend/recommendations

Returns ranked hotel recommendations for the given preferences. The body may
be empty (returns general recommendations) or contain any subset of filters.

**Request Body (optional filters):**
```json
{
  "place": "Rio de Janeiro (RJ)",
  "max_price_per_day": 200,
  "days": 3,
  "company": "4You",
  "top_n": 5
}
```

**Fields**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| place | string | No | Destination city |
| max_price_per_day | number | No | Maximum price per night (> 0) |
| days | int | No | Length of stay (1-30); used to compute total cost |
| company | string | No | User's company (personalisation) |
| top_n | int | No | Number of results (default 5, 1-20) |

**Response (Success):**
```json
{
  "recommendations": [
    {
      "hotel_name": "Hotel CB",
      "place": "Rio de Janeiro (RJ)",
      "price_per_day": 165.99,
      "total_cost": 497.97,
      "score": 81.0,
      "reason": "Exact place match"
    }
  ],
  "total": 1,
  "filters": { "place": "Rio de Janeiro (RJ)" }
}
```

**Status Codes:** `200`, `400` (validation), `503` (catalog unavailable), `500` (recommendation failed).

---

## Error Responses

```json
{ "error": "Invalid input data", "field": "flight_type", "code": "validation_failed" }
{ "error": "Invalid JSON payload", "code": "invalid_json" }
{ "error": "Prediction failed", "code": "prediction_failed" }
```

## Example cURL Commands

```bash
# Flight price
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"from":"Recife (PE)","to":"Florianopolis (SC)","flightType":"firstClass","agency":"FlyingDrops","time":1.76,"distance":676.53,"flight_year":2019,"flight_month":9,"flight_day":26,"flight_dayofweek":3}'

# Gender
curl -X POST http://localhost:5000/api/gender/predict \
  -H "Content-Type: application/json" \
  -d '{"user name":"Robert Braun","age":33,"company":"4You"}'

# Recommendations
curl -X POST http://localhost:5000/api/recommend/recommendations \
  -H "Content-Type: application/json" \
  -d '{"place":"Rio de Janeiro (RJ)","days":3,"top_n":5}'
```
