FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY api/ api/
COPY config/ config/
COPY scripts/ scripts/

# Copy model artifacts (baked into the image for portability).
# Copies whatever artifacts are present so the build succeeds even when the
# large, ML-team-supplied flight model is not checked into the repo.
COPY artifacts/ artifacts/

# Copy documentation
COPY README.md .
COPY mlflow/README.md mlflow/

# Expose API port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default environment variables (can be overridden at runtime)
ENV MODEL_PATH=artifacts/flight_price_pipeline.joblib
ENV GENDER_MODEL_PATH=artifacts/gender_model.joblib
ENV HOTELS_CATALOG_PATH=artifacts/hotel_catalog.json
ENV MLFLOW_TRACKING_URI=http://localhost:5000
ENV API_HOST=0.0.0.0
ENV API_PORT=5000

# Run the Flask application
CMD ["python", "-m", "api.app"]
