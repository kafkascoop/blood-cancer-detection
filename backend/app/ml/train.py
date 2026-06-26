"""
ML Model Training Module for Blood Cancer Detection.

Supports training from:
1. Real CSV datasets (use --csv-cbc and --csv-img)
2. Synthetic data (default, or --generate)
3. Auto-detection: tries to find latest CSV in data/ directory

Usage:
    python -m app.ml.train                  # Auto: try CSV, fallback to synthetic
    python -m app.ml.train --generate       # Force synthetic data generation
    python -m app.ml.train --export         # Export datasets to CSV, then train
    python -m app.ml.train --csv-cbc ./data/cbc.csv --csv-img ./data/image.csv
    python -m app.ml.train --csv-cbc ./data/cbc.csv  # Only train blood test model
    python -m app.ml.train --stats ./data/cbc.csv    # Show dataset statistics only
"""
import os
import sys
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib

from app.ml.data import (
    DATA_DIR, CBC_FEATURES, IMAGE_FEATURES,
    CLASS_LABELS, CLASS_LABEL_MAP,
    generate_cbc_samples, generate_image_samples,
    load_csv_dataset, get_latest_csv, dataset_stats,
    export_all_datasets,
)

np.random.seed(42)
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


# =============================================================================
# Blood Test Model (CBC Parameters)
# =============================================================================

def train_blood_test_model(X_train, y_train, X_test, y_test, X, y) -> Pipeline:
    """Train the blood test classifier on provided data."""
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    print("\n🔬 Training blood test model (Random Forest)...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)
    accuracy = (y_pred == y_test).mean()

    print(f"   ✅ Accuracy: {accuracy:.3f}")
    print(f"\n   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=CLASS_LABELS))
    print(f"   Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    cv_scores = cross_val_score(pipeline, X, y, cv=5)
    print(f"   Cross-validation: {cv_scores.mean():.3f} (+/- {cv_scores.std()*2:.3f})")

    # Save
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, "blood_test_model.pkl")
    joblib.dump(pipeline, path)
    print(f"   💾 Blood test model saved to: {path}")
    return pipeline


# =============================================================================
# Image Analysis Model
# =============================================================================

def train_image_model(X_train, y_train, X_test, y_test, X, y) -> Pipeline:
    """Train the image analysis classifier on provided data."""
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", GradientBoostingClassifier(
            n_estimators=150,
            max_depth=8,
            min_samples_split=5,
            learning_rate=0.1,
            random_state=42,
        )),
    ])

    print("\n🖼️  Training image analysis model (Gradient Boosting)...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    accuracy = (y_pred == y_test).mean()

    print(f"   ✅ Accuracy: {accuracy:.3f}")
    print(f"\n   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=CLASS_LABELS))
    print(f"   Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    cv_scores = cross_val_score(pipeline, X, y, cv=5)
    print(f"   Cross-validation: {cv_scores.mean():.3f} (+/- {cv_scores.std()*2:.3f})")

    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, "image_model.pkl")
    joblib.dump(pipeline, path)
    print(f"   💾 Image model saved to: {path}")
    return pipeline


# =============================================================================
# Dataset Preparation
# =============================================================================

def prepare_blood_test_data(source: str = "auto", csv_path: str = None, n_per_class: int = 800):
    """
    Prepare CBC dataset from CSV or synthetic generation.
    Returns (X_train, y_train, X_test, y_test, X, y)
    """
    if source == "csv" and csv_path:
        print(f"\n📂 Loading CBC dataset from: {csv_path}")
        X, y = load_csv_dataset(csv_path, CBC_FEATURES)
        if y is None:
            raise ValueError("CSV must contain a 'target' column for training")
    elif source == "csv_auto":
        latest = get_latest_csv(DATA_DIR, "cbc_dataset")
        if latest:
            print(f"\n📂 Auto-detected CBC dataset: {latest}")
            X, y = load_csv_dataset(latest, CBC_FEATURES)
        else:
            print(f"\n⚙️  No CBC dataset found. Generating synthetic data...")
            df = generate_cbc_samples(n_per_class=n_per_class)
            X, y = df[CBC_FEATURES], df["target"].map(CLASS_LABEL_MAP)
    else:  # synthetic
        print(f"\n⚙️  Generating synthetic CBC data ({n_per_class} per class)...")
        df = generate_cbc_samples(n_per_class=n_per_class)
        X, y = df[CBC_FEATURES], df["target"].map(CLASS_LABEL_MAP)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    return X_train, y_train, X_test, y_test, X, y


def prepare_image_data(source: str = "auto", csv_path: str = None, n_per_class: int = 800):
    """
    Prepare image feature dataset from CSV or synthetic generation.
    Returns (X_train, y_train, X_test, y_test, X, y)
    """
    if source == "csv" and csv_path:
        print(f"\n📂 Loading image dataset from: {csv_path}")
        X, y = load_csv_dataset(csv_path, IMAGE_FEATURES)
        if y is None:
            raise ValueError("CSV must contain a 'target' column for training")
    elif source == "csv_auto":
        latest = get_latest_csv(DATA_DIR, "image_dataset")
        if latest:
            print(f"\n📂 Auto-detected image dataset: {latest}")
            X, y = load_csv_dataset(latest, IMAGE_FEATURES)
        else:
            print(f"\n⚙️  No image dataset found. Generating synthetic data...")
            df = generate_image_samples(n_per_class=n_per_class)
            X, y = df[IMAGE_FEATURES], df["target"].map(CLASS_LABEL_MAP)
    else:  # synthetic
        print(f"\n⚙️  Generating synthetic image data ({n_per_class} per class)...")
        df = generate_image_samples(n_per_class=n_per_class)
        X, y = df[IMAGE_FEATURES], df["target"].map(CLASS_LABEL_MAP)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    return X_train, y_train, X_test, y_test, X, y


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="HematoScan ML Model Training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m app.ml.train                     # Auto-detect CSV or use synthetic
  python -m app.ml.train --generate          # Force synthetic data
  python -m app.ml.train --export            # Export CSV datasets + train
  python -m app.ml.train --csv-cbc data.csv  # Train from your own CSV
  python -m app.ml.train --csv-cbc cbc.csv --csv-img img.csv
  python -m app.ml.train --stats data.csv    # Analyze a dataset
  python -m app.ml.train --samples 5000      # Generate more synthetic samples
        """,
    )
    parser.add_argument("--generate", action="store_true", help="Force synthetic data generation")
    parser.add_argument("--export", action="store_true", help="Export datasets to CSV first")
    parser.add_argument("--csv-cbc", type=str, help="Path to CBC dataset CSV")
    parser.add_argument("--csv-img", type=str, help="Path to image feature dataset CSV")
    parser.add_argument("--samples", type=int, default=800, help="Samples per class (default: 800)")
    parser.add_argument("--stats", type=str, help="Show statistics for a dataset CSV")
    parser.add_argument("--no-image", action="store_true", help="Skip image model training")
    parser.add_argument("--no-blood", action="store_true", help="Skip blood test model training")

    args = parser.parse_args()

    print("=" * 60)
    print("🧬 HematoScan ML Model Training Pipeline")
    print("=" * 60)

    # Handle --stats mode
    if args.stats:
        dataset_stats(args.stats)
        return

    # Handle --export mode
    if args.export:
        export_all_datasets(n_per_class=args.samples)

    # Determine data source
    use_synthetic = args.generate or (not args.csv_cbc and not args.csv_img)

    # Train blood test model
    if not args.no_blood:
        if args.csv_cbc:
            data = prepare_blood_test_data(source="csv", csv_path=args.csv_cbc, n_per_class=args.samples)
        elif use_synthetic:
            data = prepare_blood_test_data(source="synthetic", n_per_class=args.samples)
        else:
            data = prepare_blood_test_data(source="csv_auto", n_per_class=args.samples)
        X_train, y_train, X_test, y_test, X, y = data
        train_blood_test_model(X_train, y_train, X_test, y_test, X, y)

    # Train image model
    if not args.no_image:
        if args.csv_img:
            data = prepare_image_data(source="csv", csv_path=args.csv_img, n_per_class=args.samples)
        elif use_synthetic:
            data = prepare_image_data(source="synthetic", n_per_class=args.samples)
        else:
            data = prepare_image_data(source="csv_auto", n_per_class=args.samples)
        X_train, y_train, X_test, y_test, X, y = data
        train_image_model(X_train, y_train, X_test, y_test, X, y)

    print("\n" + "=" * 60)
    print("✅ Training complete! Models saved to:", MODELS_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
