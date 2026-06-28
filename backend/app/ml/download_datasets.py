"""
HematoScan Dataset Downloader
==============================
Downloads blood cancer image datasets from Kaggle and organizes them
into the expected directory structure for training.

Supported datasets:
  - andrewmvd/leukemia-classification      (ALL vs Normal)
  - andrewmvd/malignant-lymphoma-classification (CLL, FL, MCL)
  - sbilab/segpc2021dataset                (Multiple Myeloma)
  - mehradaria/leukemia                     (ALL sub-types)
  - andrewmvd/bone-marrow-cell-classification (170K cells, 13+ types)

Usage:
  1. Get your Kaggle API key:
     - Go to https://www.kaggle.com/settings -> API -> Create New Token
     - Save the downloaded kaggle.json to ~/.kaggle/kaggle.json
     - chmod 600 ~/.kaggle/kaggle.json

  2. Run this script:
     python -m app.ml.download_datasets --dataset leukemia
     python -m app.ml.download_datasets --dataset lymphoma
     python -m app.ml.download_datasets --dataset myeloma
     python -m app.ml.download_datasets --dataset bone-marrow
     python -m app.ml.download_datasets --all          # Download all

  3. Organize into our 4-class structure:
     python -m app.ml.download_datasets --organize
"""
import os
import sys
import shutil
import argparse
import subprocess
import zipfile
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # backend/
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw_kaggle"
REAL_IMAGES_DIR = DATA_DIR / "real_images"

# Our 4 classification targets
CANCER_CLASSES = ["Normal", "Leukemia", "Lymphoma", "Myeloma"]

# ---------------------------------------------------------------------------
# Dataset Registry
# ---------------------------------------------------------------------------
DATASETS = {
    "leukemia": {
        "slug": "andrewmvd/leukemia-classification",
        "description": "ALL (Acute Lymphoblastic Leukemia) vs Normal",
        "url": "https://www.kaggle.com/datasets/andrewmvd/leukemia-classification",
        "class_map": {
            "ALL": "Leukemia",
            "normal": "Normal",
            "hem": "Normal",  # some use "hem" for healthy
        },
    },
    "lymphoma": {
        "slug": "andrewmvd/malignant-lymphoma-classification",
        "description": "Lymphoma subtypes: CLL, FL, MCL",
        "url": "https://www.kaggle.com/datasets/andrewmvd/malignant-lymphoma-classification",
        "class_map": {
            "CLL": "Lymphoma",
            "FL": "Lymphoma",
            "MCL": "Lymphoma",
        },
    },
    "myeloma": {
        "slug": "sbilab/segpc2021dataset",
        "description": "Multiple Myeloma plasma cells",
        "url": "https://www.kaggle.com/datasets/sbilab/segpc2021dataset",
        "class_map": {
            "myeloma": "Myeloma",
            "multiple myeloma": "Myeloma",
            "normal": "Normal",
        },
    },
    "leukemia-all": {
        "slug": "mehradaria/leukemia",
        "description": "ALL sub-types: Early Pre-B, Pre-B, Pro-B, Benign",
        "url": "https://www.kaggle.com/datasets/mehradaria/leukemia",
        "class_map": {
            "early pre-b": "Leukemia",
            "pre-b": "Leukemia",
            "pro-b": "Leukemia",
            "benign": "Normal",
        },
    },
    "bone-marrow": {
        "slug": "andrewmvd/bone-marrow-cell-classification",
        "description": "170K bone marrow cells, 13+ types",
        "url": "https://www.kaggle.com/datasets/andrewmvd/bone-marrow-cell-classification",
        "class_map": {
            "blast": "Leukemia",
            "leukemia": "Leukemia",
            "lymphoma": "Lymphoma",
            "myeloma": "Myeloma",
            "plasma cell": "Myeloma",
            "normal": "Normal",
            "healthy": "Normal",
            "neutrophil": "Normal",
            "lymphocyte": "Normal",
            "monocyte": "Normal",
            "eosinophil": "Normal",
            "basophil": "Normal",
        },
    },
}


# ===========================================================================
# Kaggle API helpers
# ===========================================================================

def _check_kaggle_auth() -> bool:
    """Check if Kaggle API is authenticated."""
    result = subprocess.run(
        ["kaggle", "datasets", "list", "--page-size", "1"],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        print("❌ Kaggle API not authenticated.")
        print("   Steps to fix:")
        print("   1. Go to https://www.kaggle.com/settings")
        print("   2. Scroll to API section -> Create New Token")
        print("   3. Place kaggle.json in ~/.kaggle/kaggle.json")
        print("   4. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    return True


def download_dataset(slug: str, output_dir: Path) -> Optional[Path]:
    """Download a Kaggle dataset and extract it."""
    print(f"\n📥 Downloading: {slug}")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Download
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d", slug],
            capture_output=True, text=True, timeout=120,
            cwd=str(output_dir),
        )
        if result.returncode != 0:
            print(f"❌ Download failed: {result.stderr}")
            return None

        # Find the downloaded zip
        zip_files = list(output_dir.glob("*.zip"))
        if not zip_files:
            print("❌ No zip file found after download")
            return None

        zip_path = zip_files[0]
        print(f"   Downloaded: {zip_path.name} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")

        # Extract
        extract_dir = output_dir / slug.replace("/", "_")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(str(extract_dir))
        print(f"   Extracted to: {extract_dir}")

        # Remove zip to save space
        zip_path.unlink()
        print(f"   Removed zip file")

        return extract_dir

    except subprocess.TimeoutExpired:
        print("❌ Download timed out (large dataset)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ===========================================================================
# Organize into 4-class structure
# ===========================================================================

def _match_class(folder_name: str, class_map: dict) -> Optional[str]:
    """Match a folder name to one of our 4 cancer types."""
    fname = folder_name.lower().strip().replace("_", " ").replace("-", " ")
    for keyword, target_class in class_map.items():
        if keyword.lower() in fname:
            return target_class
    return None


def organize_dataset(source_dir: Path, class_map: dict, dataset_name: str):
    """Walk through extracted dataset folders and copy files into real_images/."""
    print(f"\n🗂️  Organizing: {dataset_name}")
    source_dir = Path(source_dir)

    if not source_dir.exists():
        print(f"   ❌ Source directory not found: {source_dir}")
        return 0

    copied = 0
    # Walk through all subdirectories looking for image files
    image_exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in image_exts:
                continue

            # Get the containing folder name for class matching
            parent_dir = Path(root).name
            target_class = _match_class(parent_dir, class_map)

            if target_class is None:
                # Try matching on the filename itself
                target_class = _match_class(file, class_map)

            if target_class is None:
                # Default to the dataset's most common class
                print(f"   ⚠️  Could not classify: {parent_dir}/{file} — skipping")
                continue

            # Create target directory
            target_dir = REAL_IMAGES_DIR / target_class
            os.makedirs(target_dir, exist_ok=True)

            # Copy file (avoid name collisions)
            src_path = os.path.join(root, file)
            dst_path = os.path.join(target_dir, f"{dataset_name}_{file}")
            if not os.path.exists(dst_path):
                shutil.copy2(src_path, dst_path)
                copied += 1

    print(f"   ✅ Organized {copied} images into {REAL_IMAGES_DIR}")
    return copied


# ===========================================================================
# Stats
# ===========================================================================

def show_dataset_stats():
    """Print stats about organized real images."""
    if not REAL_IMAGES_DIR.exists():
        print("\n❌ No real images directory found. Run --organize first.")
        return

    print(f"\n{'='*60}")
    print("📊 Real Images Dataset Stats")
    print(f"{'='*60}")

    total = 0
    for cls_name in CANCER_CLASSES:
        cls_dir = REAL_IMAGES_DIR / cls_name
        if cls_dir.exists():
            count = len(list(cls_dir.glob("*.*")))
            total += count
            print(f"   {cls_name:12s}: {count:6d} images")
        else:
            print(f"   {cls_name:12s}: {'NOT FOUND':>6s}")

    print(f"{'─'*30}")
    print(f"   {'TOTAL':12s}: {total:6d} images")
    print()

    if total == 0:
        print("   ⚠️  No images found. Download datasets first with --dataset.")


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="HematoScan Kaggle Dataset Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dataset",
        choices=list(DATASETS.keys()) + ["all"],
        help="Dataset to download",
    )
    parser.add_argument("--all", action="store_true", help="Download all datasets")
    parser.add_argument(
        "--organize", action="store_true",
        help="Organize downloaded datasets into real_images/ (4-class structure)"
    )
    parser.add_argument(
        "--stats", action="store_true",
        help="Show statistics of organized datasets"
    )
    parser.add_argument(
        "--check-auth", action="store_true",
        help="Check Kaggle API authentication"
    )

    args = parser.parse_args()

    if args.check_auth:
        ok = _check_kaggle_auth()
        print("✅ Kaggle API authenticated!" if ok else "❌ Kaggle API not authenticated.")
        return

    if args.stats:
        show_dataset_stats()
        return

    if args.organize:
        if not RAW_DIR.exists():
            print("❌ No raw downloads found. Run with --dataset first.")
            return

        total_images = 0
        for dataset_name in DATASETS:
            source_dir = RAW_DIR / dataset_name.replace("/", "_")
            if source_dir.exists():
                info = DATASETS[dataset_name]
                count = organize_dataset(source_dir, info["class_map"], dataset_name)
                total_images += count

        print(f"\n{'='*60}")
        print(f"✅ Organization complete! {total_images} total images organized.")
        print(f"   Location: {REAL_IMAGES_DIR}")
        print(f"{'='*60}")
        return

    # Download
    if not args.dataset:
        parser.print_help()
        return

    # Check auth first
    if not _check_kaggle_auth():
        sys.exit(1)

    datasets_to_download = list(DATASETS.keys()) if (args.dataset == "all" or args.all) else [args.dataset]

    for name in datasets_to_download:
        info = DATASETS[name]
        print(f"\n{'='*60}")
        print(f"📦 Dataset: {name}")
        print(f"   {info['description']}")
        print(f"   {info['url']}")
        print(f"{'='*60}")

        extract_dir = download_dataset(info["slug"], RAW_DIR)
        if extract_dir:
            print(f"\n   Next step: run with --organize to classify into 4-class structure.")

    print(f"\n{'='*60}")
    print("✅ All downloads complete!")
    print(f"   Run: python -m app.ml.download_datasets --organize")
    print(f"   Run: python -m app.ml.download_datasets --stats")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
