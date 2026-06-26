"""
Data Management Module for HematoScan ML Training.

Provides:
- Synthetic data generation based on medical patterns
- CSV export/import for both blood test and image feature datasets
- Data validation for real-world CSV imports
- Dataset metadata and statistics
"""
import os
import random
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

# =============================================================================
# Constants: Feature Definitions & Medical Patterns
# =============================================================================

CBC_FEATURES = [
    "wbc", "rbc", "hemoglobin", "platelets",
    "neutrophils", "lymphocytes", "monocytes",
    "eosinophils", "basophils", "blast_cells",
]

CBC_UNITS = {
    "wbc": "×10³/µL", "rbc": "×10⁶/µL", "hemoglobin": "g/dL",
    "platelets": "×10³/µL", "neutrophils": "%", "lymphocytes": "%",
    "monocytes": "%", "eosinophils": "%", "basophils": "%", "blast_cells": "%",
}

CBC_NORMAL_RANGES = {
    "wbc": (4.5, 11.0), "rbc": (4.7, 6.1), "hemoglobin": (13.8, 17.2),
    "platelets": (150, 450), "neutrophils": (40, 80), "lymphocytes": (20, 40),
    "monocytes": (2, 10), "eosinophils": (1, 6), "basophils": (0, 1),
    "blast_cells": (0, 5),
}

# Medical patterns for each class: (means, stds) for each feature
CBC_CLASS_PATTERNS = {
    "Normal": {
        "means": [7.5, 5.2, 14.5, 250, 60, 30, 5, 2.5, 0.5, 0.5],
        "stds": [1.5, 0.4, 1.0, 50, 8, 5, 2, 1.0, 0.3, 0.5],
        "description": "Healthy blood profile — all parameters within normal ranges",
        "prevalence": "70-80% of routine screenings",
    },
    "Benign": {
        "means": [11.0, 4.5, 12.0, 180, 55, 35, 6, 3.0, 0.8, 5.0],
        "stds": [3.0, 0.5, 1.5, 60, 10, 7, 2.5, 1.2, 0.4, 2.0],
        "description": "Mild abnormalities — may indicate infection or non-cancerous conditions",
        "prevalence": "15-20% of abnormal screenings",
    },
    "Malignant": {
        "means": [18.0, 3.8, 9.5, 120, 45, 40, 7, 3.5, 1.0, 18.0],
        "stds": [5.0, 0.6, 1.8, 50, 12, 8, 3, 1.5, 0.5, 6.0],
        "description": "Highly abnormal profile — suspected leukemia/lymphoma",
        "prevalence": "5-10% of abnormal screenings",
    },
}

CLASS_LABELS = ["Normal", "Benign", "Malignant"]
CLASS_LABEL_MAP = {label: idx for idx, label in enumerate(CLASS_LABELS)}


IMAGE_FEATURES = [
    "cell_count", "cell_size_mean", "cell_size_std",
    "nucleus_ratio_mean", "nucleus_ratio_std",
    "blue_intensity", "red_intensity",
    "texture_contrast", "texture_homogeneity",
    "blast_like_cells_pct",
]

IMAGE_CLASS_PATTERNS = {
    "Normal": {
        "means": [80, 12.0, 2.0, 0.30, 0.05, 0.45, 0.35, 0.10, 0.85, 2.0],
        "stds": [10, 1.5, 0.5, 0.04, 0.02, 0.05, 0.04, 0.03, 0.05, 1.0],
        "description": "Normal cell morphology",
    },
    "Benign": {
        "means": [70, 14.0, 3.5, 0.40, 0.10, 0.40, 0.38, 0.15, 0.75, 10.0],
        "stds": [12, 2.0, 1.0, 0.06, 0.03, 0.06, 0.05, 0.04, 0.08, 3.0],
        "description": "Abnormal but non-cancerous morphology",
    },
    "Malignant": {
        "means": [60, 16.0, 5.0, 0.55, 0.15, 0.35, 0.42, 0.22, 0.60, 25.0],
        "stds": [15, 2.5, 1.5, 0.08, 0.04, 0.07, 0.06, 0.06, 0.10, 8.0],
        "description": "Highly abnormal morphology — blast cells present",
    },
}

# =============================================================================
# Synthetic Data Generation
# =============================================================================

def generate_cbc_samples(n_per_class: int = 1000) -> pd.DataFrame:
    """Generate synthetic CBC data with known class labels."""
    rows = []
    for cls_name in CLASS_LABELS:
        pattern = CBC_CLASS_PATTERNS[cls_name]
        for _ in range(n_per_class):
            sample = np.random.normal(pattern["means"], pattern["stds"])
            sample = np.clip(sample, [0.1, 0.1, 3, 10, 5, 5, 0.5, 0.1, 0.1, 0], None)
            rows.append({**dict(zip(CBC_FEATURES, sample)), "target": cls_name})
    return pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)


def generate_image_samples(n_per_class: int = 1000) -> pd.DataFrame:
    """Generate synthetic image feature data with known class labels."""
    rows = []
    for cls_name in CLASS_LABELS:
        pattern = IMAGE_CLASS_PATTERNS[cls_name]
        for _ in range(n_per_class):
            sample = np.random.normal(pattern["means"], pattern["stds"])
            sample = np.clip(sample, [1, 1, 0.1, 0.05, 0.01, 0.1, 0.1, 0.01, 0.1, 0], None)
            rows.append({**dict(zip(IMAGE_FEATURES, sample)), "target": cls_name})
    return pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)


# =============================================================================
# CSV Export / Import
# =============================================================================

def export_cbc_dataset(n_per_class: int = 2000, output_dir: Optional[str] = None) -> str:
    """Generate and export CBC dataset to CSV with metadata."""
    output_dir = output_dir or DATA_DIR
    os.makedirs(output_dir, exist_ok=True)

    df = generate_cbc_samples(n_per_class=n_per_class)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"cbc_dataset_{timestamp}.csv")
    df.to_csv(path, index=False)
    print(f"\n📊 Exported CBC dataset to: {path}")
    print(f"   Samples: {len(df)} ({', '.join(f'{n}: {len(df[df.target==n])}' for n in CLASS_LABELS)})")
    return path


def export_image_dataset(n_per_class: int = 2000, output_dir: Optional[str] = None) -> str:
    """Generate and export image feature dataset to CSV with metadata."""
    output_dir = output_dir or DATA_DIR
    os.makedirs(output_dir, exist_ok=True)

    df = generate_image_samples(n_per_class=n_per_class)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"image_dataset_{timestamp}.csv")
    df.to_csv(path, index=False)
    print(f"\n🖼️  Exported image dataset to: {path}")
    print(f"   Samples: {len(df)} ({', '.join(f'{n}: {len(df[df.target==n])}' for n in CLASS_LABELS)})")
    return path


def export_all_datasets(n_per_class: int = 2000) -> tuple[str, str]:
    """Export both CBC and image datasets."""
    print("=" * 60)
    print("📦 HematoScan Dataset Export")
    print("=" * 60)
    print(f"\nGenerating {n_per_class} samples per class ({n_per_class * 3} total per dataset)...")

    cbc_path = export_cbc_dataset(n_per_class)
    img_path = export_image_dataset(n_per_class)

    print(f"\n✅ Exported 2 datasets to: {DATA_DIR}")
    print(f"   CBC dataset:  {os.path.basename(cbc_path)}")
    print(f"   Image dataset: {os.path.basename(img_path)}")
    print(f"\n📋 To train from these CSVs:")
    print(f"   python -m app.ml.train --csv-cbc {cbc_path} --csv-img {img_path}")
    return cbc_path, img_path


def load_csv_dataset(
    csv_path: str,
    feature_columns: list[str],
    label_column: str = "target",
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Load a CSV dataset for training.
    Validates columns and handles common preprocessing.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    # Validate required columns
    missing_features = [c for c in feature_columns if c not in df.columns]
    if missing_features:
        raise ValueError(
            f"Missing feature columns in CSV: {missing_features}. "
            f"Expected: {feature_columns}"
        )
    if label_column not in df.columns:
        # If no label column, it might be inference-only data
        print(f"  ⚠️  No '{label_column}' column found — returning features only")
        return df[feature_columns], None

    # Validate and map labels
    X = df[feature_columns].copy()
    y = df[label_column].copy()

    # Map string labels to integers if needed
    if y.dtype == "object":
        valid_labels = set(CLASS_LABELS)
        found_labels = set(y.unique())
        unknown = found_labels - valid_labels
        if unknown:
            print(f"  ⚠️  Unknown labels found: {unknown}. Mapping them to 'Benign'.")
            y = y.apply(lambda v: v if v in valid_labels else "Benign")
        y = y.map(CLASS_LABEL_MAP)

    print(f"\n📂 Loaded dataset: {os.path.basename(csv_path)}")
    print(f"   Samples: {len(df)}")
    print(f"   Features: {len(feature_columns)}")
    print(f"   Classes: {dict(zip(*np.unique(y, return_counts=True)))}")

    return X, y


def get_latest_csv(directory: str, prefix: str) -> Optional[str]:
    """Get the most recent CSV file matching a prefix."""
    candidates = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.startswith(prefix) and f.endswith(".csv")
    ]
    return max(candidates, key=os.path.getmtime) if candidates else None


# =============================================================================
# Image Feature Extraction (OpenCV)
# =============================================================================

def extract_image_features(image_path: str) -> np.ndarray:
    """
    Extract quantitative features from a blood smear image using OpenCV.
    Returns a feature vector matching IMAGE_FEATURES.
    """
    import cv2

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blue_channel = img[:, :, 0]
    red_channel = img[:, :, 2]

    # 1. Cell count estimate via contour detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cell_contours = [c for c in contours if cv2.contourArea(c) > 20]
    cell_count = len(cell_contours)

    # 2. Cell size statistics
    cell_sizes = [cv2.contourArea(c) for c in cell_contours] if cell_contours else [0]
    cell_size_mean = float(np.mean(cell_sizes)) if cell_sizes else 0
    cell_size_std = float(np.std(cell_sizes)) if len(cell_sizes) > 1 else 0

    # 3. Nucleus-to-cytoplasm ratio (darker regions = nuclei)
    _, nucleus_thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
    nucleus_area = np.sum(nucleus_thresh > 0)
    total_cell_area = np.sum(thresh > 0)
    nucleus_ratio_mean = nucleus_area / max(total_cell_area, 1)

    # 4. Color intensities
    blue_intensity = float(np.mean(blue_channel)) / 255.0
    red_intensity = float(np.mean(red_channel)) / 255.0

    # 5. Texture features
    texture_contrast = float(gray.std()) / 255.0
    texture_homogeneity = 1.0 - texture_contrast

    # 6. Blast-like cell percentage
    blast_like = 0
    for c in cell_contours:
        area = cv2.contourArea(c)
        if area > 50:
            x, y, w, h = cv2.boundingRect(c)
            roi = gray[y:y+h, x:x+w]
            roi_nucleus = np.sum(roi < 80)
            roi_ratio = roi_nucleus / max(roi.size, 1)
            if roi_ratio > 0.5:
                blast_like += 1
    blast_pct = (blast_like / max(len(cell_contours), 1)) * 100

    return np.array([
        cell_count,
        cell_size_mean,
        min(cell_size_std, 50),
        nucleus_ratio_mean,
        0.05,  # nucleus_ratio_std (constant estimate)
        blue_intensity,
        red_intensity,
        texture_contrast,
        texture_homogeneity,
        min(blast_pct, 50),
    ])


def dataset_stats(csv_path: str) -> dict:
    """Print and return statistics for a dataset CSV."""
    df = pd.read_csv(csv_path)
    stats = {
        "file": os.path.basename(csv_path),
        "samples": len(df),
        "features": len(df.columns) - 1,
        "classes": df["target"].value_counts().to_dict() if "target" in df.columns else {},
        "missing_values": df.isnull().sum().to_dict(),
    }
    print(f"\n📊 Dataset Statistics: {os.path.basename(csv_path)}")
    print(f"   Total samples: {stats['samples']}")
    print(f"   Features: {stats['features']}")
    print(f"   Class distribution: {stats['classes']}")
    null_cols = {k: v for k, v in stats["missing_values"].items() if v > 0}
    if null_cols:
        print(f"   ⚠️  Missing values: {null_cols}")
    else:
        print(f"   ✅ No missing values")
    return stats
