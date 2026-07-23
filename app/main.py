"""
FastAPI model-serving app.

Endpoints:
    GET  /health    -> liveness/readiness probe target for Kubernetes
    POST /predict   -> run inference
    GET  /metrics   -> Prometheus metrics (via prometheus-fastapi-instrumentator)
"""

import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")

app = FastAPI(title="ML Model Serving API", version="1.0.0")

# Exposes /metrics automatically in Prometheus format
Instrumentator().instrument(app).expose(app)

_bundle = None


@app.on_event("startup")
def load_model():
    global _bundle
    _bundle = joblib.load(MODEL_PATH)


class PredictRequest(BaseModel):
    # Iris features, in order: sepal length, sepal width, petal length, petal width (cm)
    features: list[float] = Field(
        ..., min_length=4, max_length=4,
        description="4 floats: sepal_length, sepal_width, petal_length, petal_width",
    )


class PredictResponse(BaseModel):
    predicted_class: str
    class_index: int
    probabilities: dict[str, float]


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _bundle is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if _bundle is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    model = _bundle["model"]
    target_names = _bundle["target_names"]

    X = np.array(req.features).reshape(1, -1)
    pred_idx = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]

    return PredictResponse(
        predicted_class=target_names[pred_idx],
        class_index=pred_idx,
        probabilities={target_names[i]: float(p) for i, p in enumerate(proba)},
    )
