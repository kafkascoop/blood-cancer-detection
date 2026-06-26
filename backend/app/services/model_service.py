"""
Model Service: Loads trained ML models and runs inference.

Handles model loading with caching, prediction orchestration,
and fallback logic if models aren't available.
"""
import os
import logging
from typing import Optional

import numpy as np
import pandas as pd
import joblib

from app.models.detection import BloodTestData
from app.ml.data import CBC_FEATURES, IMAGE_FEATURES, extract_image_features

logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "models")
BLOOD_TEST_MODEL_PATH = os.path.join(MODELS_DIR, "blood_test_model.pkl")
IMAGE_MODEL_PATH = os.path.join(MODELS_DIR, "image_model.pkl")

# Model cache
_blood_test_model: Optional[object] = None
_image_model: Optional[object] = None


def _load_blood_test_model() -> Optional[object]:
    """Load the blood test model with caching."""
    global _blood_test_model
    if _blood_test_model is not None:
        return _blood_test_model
    if not os.path.exists(BLOOD_TEST_MODEL_PATH):
        logger.warning(f"Blood test model not found at {BLOOD_TEST_MODEL_PATH}")
        return None
    try:
        _blood_test_model = joblib.load(BLOOD_TEST_MODEL_PATH)
        logger.info("Loaded blood test model")
        return _blood_test_model
    except Exception as e:
        logger.error(f"Failed to load blood test model: {e}")
        return None


def _load_image_model() -> Optional[object]:
    """Load the image model with caching."""
    global _image_model
    if _image_model is not None:
        return _image_model
    if not os.path.exists(IMAGE_MODEL_PATH):
        logger.warning(f"Image model not found at {IMAGE_MODEL_PATH}")
        return None
    try:
        _image_model = joblib.load(IMAGE_MODEL_PATH)
        logger.info("Loaded image model")
        return _image_model
    except Exception as e:
        logger.error(f"Failed to load image model: {e}")
        return None


def predict_blood_test(data: BloodTestData) -> tuple[str, float]:
    """
    Predict blood cancer risk from CBC parameters using trained model.
    Returns (prediction_label, confidence_score).
    Raises RuntimeError if model is unavailable.
    """
    model = _load_blood_test_model()
    if model is None:
        raise RuntimeError("Blood test model not available")

    features = pd.DataFrame([[
        data.wbc, data.rbc, data.hemoglobin, data.platelets,
        data.neutrophils, data.lymphocytes, data.monocytes,
        data.eosinophils, data.basophils, data.blast_cells,
    ]], columns=CBC_FEATURES)

    try:
        class_idx = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = float(probabilities[class_idx])
        label = ["Normal", "Benign", "Malignant"][class_idx]
        return label, round(confidence, 4)
    except Exception as e:
        logger.error(f"Blood test prediction failed: {e}")
        raise RuntimeError(f"Prediction error: {e}")


def predict_from_image_file(image_path: str) -> tuple[str, float]:
    """
    Predict blood cancer risk from blood smear image using trained model.
    Returns (prediction_label, confidence_score).
    Raises RuntimeError if model is unavailable.
    """
    model = _load_image_model()
    if model is None:
        raise RuntimeError("Image model not available")

    try:
        features = extract_image_features(image_path)
        features_df = pd.DataFrame([features], columns=IMAGE_FEATURES)

        class_idx = model.predict(features_df)[0]
        probabilities = model.predict_proba(features_df)[0]
        confidence = float(probabilities[class_idx])
        label = ["Normal", "Benign", "Malignant"][class_idx]
        return label, round(confidence, 4)
    except Exception as e:
        logger.error(f"Image prediction failed: {e}")
        raise RuntimeError(f"Prediction error: {e}")


def models_available() -> bool:
    """Check if trained models exist on disk (not necessarily loaded)."""
    return os.path.exists(BLOOD_TEST_MODEL_PATH) and os.path.exists(IMAGE_MODEL_PATH)
