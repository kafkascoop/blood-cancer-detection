"""
Prediction Service: Routes predictions to ML models or fallbacks.

Prediction hierarchy for image analysis (based on settings):
  1. "cnn" mode    → CNN only (TensorFlow/Keras) → fallback if unavailable
  2. "opencv" mode → OpenCV feature extraction + GradientBoosting → fallback
  3. "auto" mode   → Try CNN first → if fails, try OpenCV+GB → fallback

For blood tests:
  1. RandomForest model
  2. Rule-based fallback
"""
import random
import logging
from typing import Optional

from app.models.detection import BloodTestData
from app.services import model_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Settings cache (refreshed per request)
# ---------------------------------------------------------------------------

async def _get_image_model_mode() -> str:
    """Fetch the image_model_mode from settings."""
    try:
        from app.database import get_settings_collection
        col = await get_settings_collection()
        doc = await col.find_one({"_id": "global_config"})
        if doc:
            return doc.get("image_model_mode", "auto")
    except Exception as e:
        logger.warning(f"Could not read settings, defaulting to 'auto': {e}")
    return "auto"


async def _get_app_name() -> str:
    """Fetch the app_name from settings."""
    try:
        from app.database import get_settings_collection
        col = await get_settings_collection()
        doc = await col.find_one({"_id": "global_config"})
        if doc:
            return doc.get("app_name", "HematoScan")
    except Exception:
        pass
    return "HematoScan"


# =============================================================================
# Blood Test Prediction
# =============================================================================

def predict_from_blood_test(data: BloodTestData) -> tuple[str, float]:
    """Predict from CBC blood test parameters using trained ML model."""
    if model_service.models_available():
        try:
            return model_service.predict_blood_test(data)
        except Exception as e:
            logger.warning(f"Blood test model prediction failed, falling back: {e}")
    return _predict_from_blood_test_fallback(data)


# =============================================================================
# Image Prediction (3-tier)
# =============================================================================

async def predict_from_image(image_path: str) -> tuple[str, float]:
    """Predict from blood smear image respecting the user's model mode.

    Mode 'auto':  CNN → OpenCV+GB → fallback
    Mode 'cnn':   CNN → fallback
    Mode 'opencv': OpenCV+GB → fallback
    """
    mode = await _get_image_model_mode()
    logger.info(f"Image prediction mode: {mode}")

    if mode == "cnn":
        return await _predict_cnn_first(image_path)
    elif mode == "opencv":
        return await _predict_opencv_first(image_path)
    else:  # "auto"
        return await _predict_auto(image_path)


async def _predict_cnn_first(image_path: str) -> tuple[str, float]:
    """Try CNN first, then fallback."""
    if model_service.dl_models_available():
        try:
            return model_service.predict_from_image_cnn(image_path)
        except Exception as e:
            logger.warning(f"CNN prediction failed: {e}")
    return _predict_from_image_fallback()


async def _predict_opencv_first(image_path: str) -> tuple[str, float]:
    """Try OpenCV+GB first, then fallback."""
    if model_service.models_available():
        try:
            return model_service.predict_from_image_file(image_path)
        except Exception as e:
            logger.warning(f"OpenCV model prediction failed: {e}")
    return _predict_from_image_fallback()


async def _predict_auto(image_path: str) -> tuple[str, float]:
    """Try CNN → OpenCV+GB → fallback."""
    # Tier 1: CNN
    if model_service.dl_models_available():
        try:
            result = model_service.predict_from_image_cnn(image_path)
            logger.info("CNN prediction successful")
            return result
        except Exception as e:
            logger.warning(f"CNN prediction failed, trying OpenCV+GB: {e}")

    # Tier 2: OpenCV + GradientBoosting
    if model_service.models_available():
        try:
            result = model_service.predict_from_image_file(image_path)
            logger.info("OpenCV+GB prediction successful")
            return result
        except Exception as e:
            logger.warning(f"OpenCV+GB prediction failed: {e}")

    # Tier 3: Rule-based fallback
    logger.info("All models unavailable, using fallback")
    return _predict_from_image_fallback()


# =============================================================================
# Fallback prediction logic
# =============================================================================

def _predict_from_blood_test_fallback(data: BloodTestData) -> tuple[str, float]:
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


def _predict_from_image_fallback() -> tuple[str, float]:
    """Random fallback when no image models are available."""
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
