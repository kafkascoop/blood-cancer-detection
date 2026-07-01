"""
Model Service: Loads trained ML models and runs inference.

Handles model loading with caching for:
  1. Scikit-learn models (GradientBoosting for images, RandomForest for CBC)
  2. CNN deep learning model (TensorFlow/Keras, if available)

Prediction follows a tiered approach based on settings.
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
CNN_MODEL_PATH = os.path.join(MODELS_DIR, "cnn_image_model.keras")

# ---------------------------------------------------------------------------
# Model caches
# ---------------------------------------------------------------------------
_blood_test_model: Optional[object] = None
_image_model: Optional[object] = None
_cnn_model: Optional[object] = None
_cnn_available: Optional[bool] = None  # cached availability check


# =============================================================================
# Blood Test Model (scikit-learn RandomForest)
# =============================================================================

def _load_blood_test_model() -> Optional[object]:
    global _blood_test_model
    if _blood_test_model is not None:
        return _blood_test_model
    if not os.path.exists(BLOOD_TEST_MODEL_PATH):
        logger.warning(f"Blood test model not found at {BLOOD_TEST_MODEL_PATH}")
        return None
    try:
        _blood_test_model = joblib.load(BLOOD_TEST_MODEL_PATH)
        logger.info("Loaded blood test model (RandomForest)")
        return _blood_test_model
    except Exception as e:
        logger.error(f"Failed to load blood test model: {e}")
        return None


# =============================================================================
# Image Model (scikit-learn GradientBoosting - OpenCV features)
# =============================================================================

def _load_image_model() -> Optional[object]:
    global _image_model
    if _image_model is not None:
        return _image_model
    if not os.path.exists(IMAGE_MODEL_PATH):
        logger.warning(f"Image model not found at {IMAGE_MODEL_PATH}")
        return None
    try:
        _image_model = joblib.load(IMAGE_MODEL_PATH)
        logger.info("Loaded image model (GradientBoosting)")
        return _image_model
    except Exception as e:
        logger.error(f"Failed to load image model: {e}")
        return None


# =============================================================================
# CNN Model (TensorFlow/Keras)
# =============================================================================

def cnn_is_available() -> bool:
    """Check if the CNN model file exists and TensorFlow is importable."""
    global _cnn_available
    if _cnn_available is not None:
        return _cnn_available
    try:
        import tensorflow  # noqa: F401
        if os.path.exists(CNN_MODEL_PATH):
            _cnn_available = True
        else:
            logger.info(f"CNN model not found at {CNN_MODEL_PATH}")
            _cnn_available = False
    except ImportError:
        logger.info("TensorFlow is not installed - CNN unavailable")
        _cnn_available = False
    return _cnn_available


def _load_cnn_model() -> Optional[object]:
    global _cnn_model
    if _cnn_model is not None:
        return _cnn_model
    if not cnn_is_available():
        return None
    try:
        from tensorflow import keras
        _cnn_model = keras.models.load_model(CNN_MODEL_PATH)
        logger.info("Loaded CNN model (TensorFlow/Keras)")
        return _cnn_model
    except Exception as e:
        logger.error(f"Failed to load CNN model: {e}")
        return None


# =============================================================================
# Prediction Functions
# =============================================================================

def predict_blood_test(data: BloodTestData | dict) -> tuple[str, float]:
    """Predict blood cancer risk from CBC parameters using RandomForest."""
    # Accept both BloodTestData objects and plain dicts
    if isinstance(data, dict):
        data = BloodTestData.model_validate(data)
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
        label = ["Normal", "Leukemia", "Lymphoma", "Myeloma"][class_idx]
        return label, round(confidence, 4)
    except Exception as e:
        logger.error(f"Blood test prediction failed: {e}")
        raise RuntimeError(f"Prediction error: {e}")


def predict_from_image_file(image_path: str) -> tuple[str, float]:
    """Predict from blood smear image using OpenCV + GradientBoosting."""
    model = _load_image_model()
    if model is None:
        raise RuntimeError("OpenCV image model not available")

    try:
        features = extract_image_features(image_path)
        features_df = pd.DataFrame([features], columns=IMAGE_FEATURES)

        class_idx = model.predict(features_df)[0]
        probabilities = model.predict_proba(features_df)[0]
        confidence = float(probabilities[class_idx])
        label = ["Normal", "Leukemia", "Lymphoma", "Myeloma"][class_idx]
        return label, round(confidence, 4)
    except Exception as e:
        logger.error(f"Image prediction failed: {e}")
        raise RuntimeError(f"Prediction error: {e}")


def predict_from_image_cnn(image_path: str) -> tuple[str, float]:
    """Predict from blood smear image using the CNN model directly.

    Uses PIL for image loading (avoids deprecated keras.preprocessing.image).
    Automatically detects model type by name:
      - "hematoscan_cnn_pretrained" → has preprocess_input baked in → [0, 255]
      - "hematoscan_cnn" → scratch CNN, trained on [0, 1] → [0, 1]
    Returns (label, confidence).
    Raises RuntimeError if CNN model is unavailable.
    """
    model = _load_cnn_model()
    if model is None:
        raise RuntimeError("CNN model not available")

    try:
        import numpy as np
        from PIL import Image

        pil_img = Image.open(image_path).convert("RGB").resize((224, 224))
        img_array = np.array(pil_img, dtype=np.float32)

        # Detect model type from name
        is_pretrained = getattr(model, "name", "").endswith("_pretrained")

        if is_pretrained:
            # pretrained: preprocess_input is baked in, expects [0, 255]
            pass  # keep raw [0, 255]
        else:
            # scratch: trained on [0, 1] data, expects [0, 1]
            img_array = img_array / 255.0

        img_array = np.expand_dims(img_array, axis=0)

        probs = model.predict(img_array, verbose=0)[0]
        class_idx = int(np.argmax(probs))
        confidence = float(probs[class_idx])
        label = ["Normal", "Leukemia", "Lymphoma", "Myeloma"][class_idx]
        return label, round(confidence, 4)
    except Exception as e:
        logger.error(f"CNN prediction failed: {e}")
        raise RuntimeError(f"CNN prediction error: {e}")


# =============================================================================
# Availability Checks
# =============================================================================

def models_available() -> bool:
    """Check if scikit-learn models exist on disk."""
    return os.path.exists(BLOOD_TEST_MODEL_PATH) and os.path.exists(IMAGE_MODEL_PATH)


def dl_models_available() -> bool:
    """Check if deep learning models exist on disk."""
    return cnn_is_available()
