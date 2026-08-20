"""Input schema for flight price prediction requests."""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional
import re


class FlightPredictionInput(BaseModel):
    """Schema for flight price prediction input."""

    # Flight-specific features (placeholder - will be updated from model artifact)
    flight_duration: float = Field(
        ..., gt=0, description="Duration of the flight in hours"
    )
    distance: float = Field(..., gt=0, description="Distance in kilometers")
    airline: str = Field(..., min_length=1, description="Airline code/name")
    departure_hour: int = Field(..., ge=0, le=23, description="Departure hour (0-23)")
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday)")
    is_weekend: bool = Field(default=False, description="Whether it's a weekend flight")
    is_holiday: bool = Field(default=False, description="Whether it's a holiday period")
    days_until_departure: int = Field(
        ..., gt=0, description="Days until flight departure"
    )
    class_type: str = Field(..., pattern="^(economy|business|first)$")
    origin_airport: str = Field(..., min_length=3, max_length=4)
    destination_airport: str = Field(..., min_length=3, max_length=4)

    @field_validator("airline", mode="before")
    @classmethod
    def validate_airline(cls, v: str) -> str:
        """Validate airline name."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Airline cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
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
        }


class FlightPredictionOutput(BaseModel):
    """Schema for flight price prediction output."""

    predicted_price: float = Field(..., description="Predicted flight price")
    model_version: Optional[str] = Field(
        None, description="Version of the model used"
    )
    model_name: Optional[str] = Field(None, description="Name of the model used")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted_price": 450.75,
                "model_version": "1.0",
                "model_name": "flight_price_regression",
            }
        }


class HealthCheck(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Health status")

    class Config:
        json_schema_extra = {"example": {"status": "healthy"}}


class ModelInfo(BaseModel):
    """Schema for model info response."""

    model_name: Optional[str] = Field(None, description="Name of the loaded model")
    model_version: Optional[str] = Field(None, description="Version of the model")
    status: str = Field(..., description="Model loading status")

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "flight_price_regression",
                "model_version": "1.0",
                "status": "loaded",
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    code: str = Field(..., description="Error code")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation failed",
                "field": "departure_hour",
                "code": "invalid_value",
            }
        }
