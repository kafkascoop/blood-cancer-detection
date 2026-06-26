"""
Prediction Service: Routes predictions to ML models or fallbacks.

This is the public API for predictions. It tries to use trained ML models
first, and falls back to rule-based simulation if models aren't loaded.
"""
import random
from app.models.detection import BloodTestData
from app.services import model_service


def predict_from_blood_test(data: BloodTestData) -> tuple[str, float]:
    """
    Predict from CBC blood test parameters using trained ML model.
    Falls back to simulation if model unavailable.
    """
    if model_service.models_available():
        return model_service.predict_blood_test(data)
    return predict_from_blood_test_fallback(data)


def predict_from_image(image_path: str) -> tuple[str, float]:
    """
    Predict from blood smear image using trained ML model.
    Falls back to simulation if model unavailable.
    """
    if model_service.models_available():
        return model_service.predict_from_image_file(image_path)
    return predict_from_image_fallback()


# =============================================================================
# Fallback prediction logic (used when ML models are not trained yet)
# =============================================================================

def predict_from_blood_test_fallback(data: BloodTestData) -> tuple[str, float]:
    """Rule-based fallback when the ML model isn't available."""
    risk_score = 0.0

    if data.blast_cells > 20:
        risk_score += 0.8
    elif data.blast_cells > 10:
        risk_score += 0.5
    elif data.blast_cells > 5:
        risk_score += 0.3

    if data.wbc > 15 or data.wbc < 3:
        risk_score += 0.2
    if data.hemoglobin < 10:
        risk_score += 0.15
    elif data.hemoglobin < 12:
        risk_score += 0.05
    if data.platelets < 100:
        risk_score += 0.2
    elif data.platelets < 150:
        risk_score += 0.1
    if data.neutrophils > 85 or data.neutrophils < 20:
        risk_score += 0.1

    noise = random.uniform(-0.05, 0.05)
    risk_score = max(0.0, min(1.0, risk_score + noise))

    if risk_score < 0.3:
        prediction = "Normal"
        confidence = 0.85 + random.uniform(0, 0.14)
    elif risk_score < 0.6:
        prediction = "Benign"
        confidence = 0.75 + random.uniform(0, 0.19)
    else:
        prediction = "Malignant"
        confidence = 0.80 + random.uniform(0, 0.15)

    confidence = min(confidence, 0.99)
    return prediction, round(confidence, 4)


def predict_from_image_fallback() -> tuple[str, float]:
    """Random fallback when the image model isn't available."""
    predictions = ["Normal", "Benign", "Malignant"]
    weights = [0.60, 0.25, 0.15]
    prediction = random.choices(predictions, weights=weights, k=1)[0]

    if prediction == "Normal":
        confidence = 0.85 + random.uniform(0, 0.14)
    elif prediction == "Benign":
        confidence = 0.75 + random.uniform(0, 0.19)
    else:
        confidence = 0.80 + random.uniform(0, 0.15)

    confidence = min(confidence, 0.99)
    return prediction, round(confidence, 4)
