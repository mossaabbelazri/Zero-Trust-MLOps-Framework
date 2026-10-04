from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Dict, Any
import pandas as pd
# pyrefly: ignore [missing-import]
import mlflow.pyfunc
import os
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="MLOps - Generic Serving API (Zero Trust)")

# Define Prometheus metrics
# We generalize the metric to count anomalies or positive classes
PREDICTION_ANOMALIES = Counter("ml_prediction_anomalies_total", "Total number of predictions classified as positive/anomaly")
TOTAL_PREDICTIONS = Counter("ml_predictions_total", "Total number of predictions made")

# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-service.default.svc.cluster.local:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

MODEL_NAME = os.getenv("MODEL_NAME", "MyGenericModel")
MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")
# Threshold for binary classification anomaly detection (if applicable)
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.5"))

model = None

@app.on_event("startup")
def load_model():
    global model
    try:
        print(f"Connecting to MLflow registry at {MLFLOW_TRACKING_URI}...")
        # Using pyfunc to support any ML framework (sklearn, xgboost, tf, etc.)
        model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")
        print("Success: Model loaded in memory from MLflow!")
    except Exception as e:
        print(f"Warning: Failed to load from MLflow ({e}).")
        # In a generic template, you can implement fallback logic here
        print("Warning: Running in degraded mode. Health checks may report issues.")

class PredictionRequest(BaseModel):
    # Accept any generic features dictionary
    features: Dict[str, Any]

@app.get("/health")
def health_check():
    if model is None:
        return {"status": "Degraded", "detail": "API is online, but MLflow model is missing."}
    return {"status": "Healthy", "detail": "API and Model are fully operational."}

@app.post("/predict")
def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not ready. Please try again later.")
        
    TOTAL_PREDICTIONS.inc()
    
    # Convert input to pandas DataFrame
    data = pd.DataFrame([request.features])
    
    try:
        # Perform prediction
        prediction = model.predict(data)
        
        # Extract the scalar value if it's a single prediction
        pred_value = prediction[0] if isinstance(prediction, (list, pd.Series, pd.DataFrame)) or hasattr(prediction, '__len__') else prediction
        
        # Basic anomaly detection logic (configurable threshold)
        try:
            is_anomaly = float(pred_value) > ANOMALY_THRESHOLD
            if is_anomaly:
                PREDICTION_ANOMALIES.inc()
        except ValueError:
            # Not a numeric prediction, ignore anomaly metrics
            pass
            
        return {
            "prediction": pred_value,
            "status": "Success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)