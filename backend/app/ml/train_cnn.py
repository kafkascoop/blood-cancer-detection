"""
CNN Model Training Module for HematoScan.

Trains a Convolutional Neural Network on blood smear images for
cancer classification (Normal / Benign / Malignant).

Requirements:
    pip install tensorflow         (requires Python < 3.13)
    pip install torch torchvision  (alternative)

Usage:
    python -m app.ml.train_cnn --data-dir ./data/images --epochs 50
    python -m app.ml.train_cnn --data-dir ./data/images --pretrained
"""
import os
import sys
import argparse
import numpy as np
from typing import Optional

# ---------------------------------------------------------------------------
# Conditional import so the app doesn't crash if TF/PyTorch isn't installed
# ---------------------------------------------------------------------------
BACKEND: Optional[str] = None  # "tensorflow" or "pytorch"

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, applications, callbacks

    BACKEND = "tensorflow"
    _HAS_TF = True
except ImportError:
    _HAS_TF = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    from torchvision import transforms, models as tv_models

    if BACKEND is None:
        BACKEND = "pytorch"
    _HAS_PT = True
except ImportError:
    _HAS_PT = False

CLASS_LABELS = ["Normal", "Benign", "Malignant"]
NUM_CLASSES = 3
IMG_SIZE = 224  # standard input size for CNNs

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
CNN_MODEL_PATH_TF = os.path.join(MODELS_DIR, "cnn_image_model.keras")
CNN_MODEL_PATH_PT = os.path.join(MODELS_DIR, "cnn_image_model.pt")


# =============================================================================
# TensorFlow / Keras CNN
# =============================================================================

def _build_tf_cnn(input_shape=(IMG_SIZE, IMG_SIZE, 3)) -> keras.Model:
    """Build a lightweight CNN for blood cell classification."""
    inputs = keras.Input(shape=input_shape, name="image")

    # Block 1
    x = layers.Rescaling(1.0 / 255)(inputs)
    x = layers.Conv2D(32, (3, 3), padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling2D((2, 2))(x)

    # Block 2
    x = layers.Conv2D(64, (3, 3), padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling2D((2, 2))(x)

    # Block 3
    x = layers.Conv2D(128, (3, 3), padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling2D((2, 2))(x)

    # Block 4
    x = layers.Conv2D(256, (3, 3), padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.GlobalAveragePooling2D()(x)

    # Classifier head
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(NUM_CLASSES, activation="softmax", name="prediction")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="hematoscan_cnn")
    return model


def _build_tf_pretrained(input_shape=(IMG_SIZE, IMG_SIZE, 3)) -> keras.Model:
    """Build a model using MobileNetV2 transfer learning."""
    base = applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # freeze base

    inputs = keras.Input(shape=input_shape)
    x = applications.mobilenet_v2.preprocess_input(inputs)
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(NUM_CLASSES, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="hematoscan_cnn_pretrained")
    return model


def train_tf_cnn(
    train_dir: str,
    val_dir: Optional[str] = None,
    epochs: int = 50,
    batch_size: int = 32,
    use_pretrained: bool = False,
):
    """Train the TensorFlow CNN on blood cell images.

    Expects subdirectories: Normal/, Benign/, Malignant/ inside train_dir.
    """
    if not _HAS_TF:
        print("❌ TensorFlow is not installed. Run: pip install tensorflow (requires Python < 3.13)")
        return

    print(f"\n{'='*60}")
    print("🧠 Training CNN (TensorFlow/Keras)")
    print(f"   Backend: {BACKEND}")
    print(f"   Device:  {'GPU' if len(tf.config.list_physical_devices('GPU')) > 0 else 'CPU'}")
    print(f"{'='*60}\n")

    # Data augmentation for training
    train_datagen = keras.preprocessing.image.ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.15,
        horizontal_flip=True,
        fill_mode="nearest",
        validation_split=0.2 if val_dir is None else 0,
    )

    if val_dir:
        # Separate validation directory provided
        train_gen = train_datagen.flow_from_directory(
            train_dir,
            target_size=(IMG_SIZE, IMG_SIZE),
            batch_size=batch_size,
            class_mode="categorical",
            classes=CLASS_LABELS,
            shuffle=True,
        )
        val_gen = keras.preprocessing.image.ImageDataGenerator(rescale=1.0 / 255).flow_from_directory(
            val_dir,
            target_size=(IMG_SIZE, IMG_SIZE),
            batch_size=batch_size,
            class_mode="categorical",
            classes=CLASS_LABELS,
            shuffle=False,
        )
    else:
        # Split from training directory
        train_gen = train_datagen.flow_from_directory(
            train_dir,
            target_size=(IMG_SIZE, IMG_SIZE),
            batch_size=batch_size,
            class_mode="categorical",
            classes=CLASS_LABELS,
            subset="training",
            shuffle=True,
        )
        val_gen = train_datagen.flow_from_directory(
            train_dir,
            target_size=(IMG_SIZE, IMG_SIZE),
            batch_size=batch_size,
            class_mode="categorical",
            classes=CLASS_LABELS,
            subset="validation",
            shuffle=False,
        )

    print(f"\n   Training samples: {train_gen.samples}")
    print(f"   Validation samples: {val_gen.samples}")

    # Build model
    model = _build_tf_pretrained() if use_pretrained else _build_tf_cnn()
    model.summary()

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3 if not use_pretrained else 1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )

    # Callbacks
    cb = [
        callbacks.EarlyStopping(patience=10, restore_best_weights=True, monitor="val_loss"),
        callbacks.ReduceLROnPlateau(factor=0.5, patience=5, min_lr=1e-6, monitor="val_loss"),
        callbacks.ModelCheckpoint(CNN_MODEL_PATH_TF, save_best_only=True, monitor="val_accuracy"),
    ]

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=epochs,
        callbacks=cb,
        verbose=1,
    )

    final_acc = max(history.history["val_accuracy"])
    print(f"\n✅ Training complete! Best validation accuracy: {final_acc:.3f}")
    print(f"   Model saved to: {CNN_MODEL_PATH_TF}")
    return model


# =============================================================================
# Prediction helpers
# =============================================================================

def load_tf_cnn() -> Optional[object]:
    """Load the trained TensorFlow CNN model."""
    if not _HAS_TF:
        return None
    if not os.path.exists(CNN_MODEL_PATH_TF):
        return None
    try:
        model = keras.models.load_model(CNN_MODEL_PATH_TF)
        return model
    except Exception as e:
        print(f"Failed to load CNN model: {e}")
        return None


def predict_tf_cnn(model: object, image_path: str) -> tuple[str, float]:
    """Run prediction on a single image using the TF CNN model.

    Returns (label, confidence).
    """
    from PIL import Image
    img = Image.open(image_path).resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img, dtype=np.float32) / 255.0
    if img_array.ndim == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    img_array = np.expand_dims(img_array, axis=0)

    probs = model.predict(img_array, verbose=0)[0]
    class_idx = int(np.argmax(probs))
    confidence = float(probs[class_idx])
    label = CLASS_LABELS[class_idx]
    return label, round(confidence, 4)


# =============================================================================
# CLI
# =============================================================================

def has_deep_learning() -> bool:
    """Check if either TensorFlow or PyTorch is available."""
    return _HAS_TF or _HAS_PT


def main():
    parser = argparse.ArgumentParser(description="HematoScan CNN Training")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to image directory (subdirs: Normal, Benign, Malignant)")
    parser.add_argument("--val-dir", type=str, default=None, help="Optional separate validation directory")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--pretrained", action="store_true", help="Use MobileNetV2 transfer learning")
    parser.add_argument("--backend", choices=["tensorflow", "pytorch"], default="tensorflow", help="Deep learning backend")

    args = parser.parse_args()

    if not _HAS_TF and not _HAS_PT:
        print("❌ No deep learning framework found.")
        print("   Install TensorFlow or PyTorch:")
        print("   pip install tensorflow        (Python < 3.13)")
        print("   pip install torch torchvision")
        sys.exit(1)

    if args.backend == "tensorflow" and _HAS_TF:
        train_tf_cnn(
            train_dir=args.data_dir,
            val_dir=args.val_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            use_pretrained=args.pretrained,
        )
    elif args.backend == "pytorch" and _HAS_PT:
        print("❌ PyTorch backend not yet implemented. Use --backend tensorflow.")
        sys.exit(1)
    else:
        print(f"❌ Backend '{args.backend}' not available.")
        sys.exit(1)


if __name__ == "__main__":
    main()
