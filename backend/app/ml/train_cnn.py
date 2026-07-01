"""
CNN Model Training Module for HematoScan.

Trains a Convolutional Neural Network on blood smear images for
blood cancer classification (Normal / Leukemia / Lymphoma / Myeloma).

Requirements:
    pip install tensorflow

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
# Conditional import so the app doesn't crash if TF isn't installed
# ---------------------------------------------------------------------------
BACKEND: Optional[str] = None

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

CLASS_LABELS = ["Normal", "Leukemia", "Lymphoma", "Myeloma"]
NUM_CLASSES = 4
IMG_SIZE = 224  # standard input size for CNNs

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
CNN_MODEL_PATH_TF = os.path.join(MODELS_DIR, "cnn_image_model.keras")


# =============================================================================
# Data Loading (modern tf.data API — no deprecated ImageDataGenerator)
# =============================================================================

def _load_dataset(data_dir: str, batch_size: int, shuffle: bool = True,
                  normalize: bool = True):
    """Load images from a directory structure using image_dataset_from_directory.

    Expects subdirectories: Normal/, Leukemia/, Lymphoma/, Myeloma/.
    When normalize=True, scales pixels to [0, 1].
    When normalize=False, keeps raw uint8 [0, 255] (needed for pretrained models
    that use preprocess_input internally).
    """
    AUTOTUNE = tf.data.AUTOTUNE

    ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=CLASS_LABELS,
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=batch_size,
        shuffle=shuffle,
        seed=42,
    )

    if normalize:
        # Scale to [0, 1] for scratch-trained models
        ds = ds.map(lambda x, y: (tf.cast(x, tf.float32) / 255.0, y),
                    num_parallel_calls=AUTOTUNE)
    else:
        # Cast to float32 but keep [0, 255] for pretrained models
        # (preprocess_input handles the scaling)
        ds = ds.map(lambda x, y: (tf.cast(x, tf.float32), y),
                    num_parallel_calls=AUTOTUNE)

    return ds.prefetch(buffer_size=AUTOTUNE)


def _augment_dataset(ds):
    """Apply data augmentation using Keras layers (not deprecated ImageDataGenerator)."""
    AUTOTUNE = tf.data.AUTOTUNE
    augmentation = keras.Sequential([
        layers.RandomRotation(0.15),
        layers.RandomTranslation(0.1, 0.1),
        layers.RandomZoom(0.15),
        layers.RandomFlip("horizontal"),
        layers.RandomContrast(0.1),
    ])

    def augment(x, y):
        return augmentation(x, training=True), y

    return ds.map(augment, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)


# =============================================================================
# TensorFlow / Keras CNN
# =============================================================================

def _build_tf_cnn(input_shape=(IMG_SIZE, IMG_SIZE, 3)) -> keras.Model:
    """Build a lightweight CNN for blood cell classification (expects [0,1] input)."""
    inputs = keras.Input(shape=input_shape, name="image")

    # Block 1
    x = layers.Conv2D(32, (3, 3), padding="same")(inputs)
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
    """Build a model using MobileNetV2 transfer learning (expects [0,255] input).

    MobileNetV2's preprocess_input handles scaling to [-1, 1], so the data
    loader should NOT divide by 255 when using this model.
    """
    base = applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # freeze base

    inputs = keras.Input(shape=input_shape)
    x = applications.mobilenet_v2.preprocess_input(inputs)  # expects [0,255]
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

    Uses the modern tf.data API (not deprecated ImageDataGenerator).
    Expects subdirectories: Normal/, Leukemia/, Lymphoma/, Myeloma/ inside train_dir.

    For pretrained models, images are NOT divided by 255 because
    MobileNetV2's preprocess_input handles normalization internally.
    """
    if not _HAS_TF:
        print("❌ TensorFlow is not installed. Run: pip install tensorflow")
        return

    print(f"\n{'='*60}")
    print("🧠 Training CNN (TensorFlow/Keras)")
    print(f"   Backend: {BACKEND}")
    print(f"   Device:  {'GPU' if len(tf.config.list_physical_devices('GPU')) > 0 else 'CPU'}")
    print(f"   Model:   {'MobileNetV2 (pretrained)' if use_pretrained else 'Scratch CNN'}")
    print(f"{'='*60}\n")

    # Pretrained models need [0, 255] input (preprocess_input handles scaling)
    should_normalize = not use_pretrained

    if val_dir:
        train_ds = _augment_dataset(
            _load_dataset(train_dir, batch_size, shuffle=True, normalize=should_normalize)
        )
        val_ds = _load_dataset(val_dir, batch_size, shuffle=False, normalize=should_normalize)
    else:
        full_ds = _load_dataset(train_dir, batch_size, shuffle=True, normalize=should_normalize)
        total_samples = sum(1 for _ in full_ds.unbatch())
        print(f"   Total samples in directory: {total_samples}")

        full_ds = full_ds.unbatch().shuffle(10000, seed=42)
        val_size = int(total_samples * 0.2)

        val_ds = full_ds.take(val_size).batch(batch_size)
        train_raw = full_ds.skip(val_size).batch(batch_size)

        val_ds = val_ds.prefetch(tf.data.AUTOTUNE)
        train_ds = _augment_dataset(train_raw)

    # Get class names from directory structure (separate call to avoid consuming the dataset)
    class_names = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        labels="inferred",
        class_names=CLASS_LABELS,
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=1,
        shuffle=False,
        seed=42,
    ).class_names

    print(f"   Classes detected: {class_names}")
    print(f"   Training samples: {sum(1 for _ in train_ds.unbatch())}")
    print(f"   Validation samples: {sum(1 for _ in val_ds.unbatch())}")

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
        train_ds,
        validation_data=val_ds,
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

    Feeds [0, 255] input and lets the model handle normalization internally.
    Returns (label, confidence).
    """
    from PIL import Image
    img = Image.open(image_path).resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img, dtype=np.float32)
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
    parser.add_argument("--data-dir", type=str, required=True,
                        help="Path to image directory (subdirs: Normal, Leukemia, Lymphoma, Myeloma)")
    parser.add_argument("--val-dir", type=str, default=None,
                        help="Optional separate validation directory")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--pretrained", action="store_true",
                        help="Use MobileNetV2 transfer learning")
    parser.add_argument("--backend", choices=["tensorflow", "pytorch"],
                        default="tensorflow", help="Deep learning backend")

    args = parser.parse_args()

    if not _HAS_TF and not _HAS_PT:
        print("❌ No deep learning framework found.")
        print("   Install TensorFlow:")
        print("   pip install tensorflow")
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
