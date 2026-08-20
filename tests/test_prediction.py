"""Test prediction endpoint."""

import pytest
import joblib
import os
from api.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def dummy_model_path():
    """Path to dummy model for testing."""
    return "tests/fixtures/dummy_model.joblib"


@pytest.fixture
def setup_dummy_model(dummy_model_path):
    """Create dummy model for testing if it doesn't exist."""
    if not os.path.exists(dummy_model_path):
        from tests.fixtures.dummy_model import create_dummy_model
        create_dummy_model(dummy_model_path)
    return dummy_model_path


@pytest.fixture
def test_input_data():
    """Sample input data for prediction."""
    return {
        "flight_duration": 5.5,
        "distance": 4500.0,
        "airline": "UA",
        "departure_hour": 14,
        "day_of_week": 2,
        "is_weekend": False,
        "is_holiday": False,
        "days_until_departure": 21,
        "class_type": "economy",
        "origin_airport": "JFK",
        "destination_airport": "LAX",
    }


def test_predict_endpoint_returns_200(client, setup_dummy_model):
    """Test prediction endpoint returns HTTP 200."""
    response = client.post(
        "/api/predict",
        json={
            "flight_duration": 5.5,
            "distance": 4500.0,
            "airline": "UA",
            "departure_hour": 14,
            "day_of_week": 2,
            "is_weekend": False,
            "is_holiday": False,
            "days_until_departure": 21,
            "class_type": "economy",
            "origin_airport": "JFK",
            "destination_airport": "LAX",
        },
    )

    assert response.status_code == 200


def test_predict_endpoint_returns_json(client, setup_dummy_model):
    """Test prediction endpoint returns JSON."""
    response = client.post("/api/predict", json=test_input_data())

    assert response.content_type == "application/json"


def test_predict_endpoint_has_predicted_price(client, setup_dummy_model):
    """Test prediction response contains predicted_price field."""
    response = client.post("/api/predict", json=test_input_data())
    json_data = response.get_json()

    assert "predicted_price" in json_data
    assert isinstance(json_data["predicted_price"], (int, float))


def test_predict_endpoint_returns_valid_price(client, setup_dummy_model):
    """Test prediction returns a reasonable price."""
    response = client.post("/api/predict", json=test_input_data())
    json_data = response.get_json()

    predicted_price = json_data["predicted_price"]
    # Check price is positive and reasonable (flight prices should be > 0)
    assert predicted_price > 0
    assert predicted_price < 100000  # Reasonable upper bound


def test_predict_endpoint_missing_field(client, setup_dummy_model):
    """Test prediction fails with missing required field."""
    incomplete_data = {
        "flight_duration": 5.5,
        "distance": 4500.0,
        # Missing required field: airline
    }

    response = client.post("/api/predict", json=incomplete_data)

    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_predict_endpoint_invalid_value(client, setup_dummy_model):
    """Test prediction fails with invalid value."""
    invalid_data = {
        "flight_duration": -5.5,  # Invalid: negative duration
        "distance": 4500.0,
        "airline": "UA",
        "departure_hour": 14,
        "day_of_week": 2,
        "is_weekend": False,
        "is_holiday": False,
        "days_until_departure": 21,
        "class_type": "economy",
        "origin_airport": "JFK",
        "destination_airport": "LAX",
    }

    response = client.post("/api/predict", json=invalid_data)

    assert response.status_code == 400


def test_predict_endpoint_invalid_json(client, setup_dummy_model):
    """Test prediction fails with invalid JSON."""
    response = client.post(
        "/api/predict",
        data="not valid json",
        content_type="application/json",
    )

    assert response.status_code == 400


def test_predict_endpoint_empty_body(client, setup_dummy_model):
    """Test prediction fails with empty body."""
    response = client.post(
        "/api/predict",
        data="{}",
        content_type="application/json",
    )

    assert response.status_code == 400


def test_predict_endpoint_with_business_class(client, setup_dummy_model):
    """Test prediction works with business class."""
    business_data = {
        "flight_duration": 5.5,
        "distance": 4500.0,
        "airline": "UA",
        "departure_hour": 14,
        "day_of_week": 2,
        "is_weekend": False,
        "is_holiday": False,
        "days_until_departure": 21,
        "class_type": "business",
        "origin_airport": "JFK",
        "destination_airport": "LAX",
    }

    response = client.post("/api/predict", json=business_data)

    assert response.status_code == 200
    json_data = response.get_json()

    # Business class should be more expensive than economy
    # We can't test exact values but should be in valid range
    assert json_data["predicted_price"] > 0
