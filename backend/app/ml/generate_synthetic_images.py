"""
Generate synthetic blood smear images for CNN training.

Creates image samples that visually correspond to the three classes
(Normal, Benign, Malignant) using the medical patterns defined in data.py.

Each image contains scattered cell-like blobs with varying:
  - Cell size (larger in malignant)
  - Nucleus ratio (larger/darker nuclei in malignant)
  - Color intensity (different staining patterns)
  - Cell density (fewer but larger cells in malignant)

Usage:
    python -m app.ml.generate_synthetic_images --output ./data/images --samples 500
"""
import os
import random
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

random.seed(42)
np.random.seed(42)

IMG_SIZE = 224
CLASS_LABELS = ["Normal", "Benign", "Malignant"]

# Medical patterns from data.py (aligned with CBC/Image patterns)
CLASS_PATTERNS = {
    "Normal": {
        "cell_count_range": (15, 25),
        "cell_size_range": (8, 16),
        "nucleus_ratio_range": (0.25, 0.35),
        "blue_intensity": (0.40, 0.50),
        "red_intensity": (0.30, 0.40),
        "blast_like_pct": (0, 5),
        "description": "Healthy cells — uniform size, small nuclei, normal density",
    },
    "Benign": {
        "cell_count_range": (10, 20),
        "cell_size_range": (12, 22),
        "nucleus_ratio_range": (0.35, 0.50),
        "blue_intensity": (0.35, 0.45),
        "red_intensity": (0.35, 0.45),
        "blast_like_pct": (5, 15),
        "description": "Abnormal but non-cancerous — larger cells, bigger nuclei",
    },
    "Malignant": {
        "cell_count_range": (5, 12),
        "cell_size_range": (18, 32),
        "nucleus_ratio_range": (0.50, 0.70),
        "blue_intensity": (0.30, 0.40),
        "red_intensity": (0.38, 0.48),
        "blast_like_pct": (20, 45),
        "description": "Malignant — few large cells, very large dark nuclei, irregular",
    },
}


def draw_cell(draw, x, y, radius, nucleus_ratio, is_blast=False):
    """Draw a single cell with nucleus at position (x, y)."""
    # Cell body (cytoplasm) — pale purple/pink
    cell_color = (
        random.randint(200, 230),  # R
        random.randint(180, 210),  # G
        random.randint(200, 230),  # B
    )
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        fill=cell_color,
        outline=(160, 140, 170),
        width=1,
    )

    # Nucleus — darker purple/blue
    nucleus_radius = int(radius * nucleus_ratio)
    if is_blast:
        # Blast cells have very large, irregular nuclei
        nucleus_color = (60, 40, 100)
    else:
        nucleus_color = (80, 60, 120)

    draw.ellipse(
        [
            x - nucleus_radius,
            y - nucleus_radius,
            x + nucleus_radius,
            y + nucleus_radius,
        ],
        fill=nucleus_color,
    )

    # Add some texture dots inside nucleus
    for _ in range(random.randint(2, 5)):
        dx = random.randint(-nucleus_radius // 2, nucleus_radius // 2)
        dy = random.randint(-nucleus_radius // 2, nucleus_radius // 2)
        dot_size = random.randint(1, 2)
        draw.ellipse(
            [x + dx - dot_size, y + dy - dot_size, x + dx + dot_size, y + dy + dot_size],
            fill=(40, 30, 70),
        )


def generate_synthetic_image(cls_name: str) -> Image.Image:
    """Generate a synthetic blood smear image for the given class."""
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), (245, 240, 248))
    draw = ImageDraw.Draw(img)

    pattern = CLASS_PATTERNS[cls_name]

    cell_count = random.randint(*pattern["cell_count_range"])
    cell_size_range = pattern["cell_size_range"]
    nucleus_ratio_range = pattern["nucleus_ratio_range"]
    blast_pct_range = pattern["blast_like_pct"]

    # Background texture (noise)
    for _ in range(500):
        x = random.randint(0, IMG_SIZE - 1)
        y = random.randint(0, IMG_SIZE - 1)
        c = random.randint(230, 250)
        img.putpixel((x, y), (c, c - 5, c + 5))

    # Place cells with some overlap avoidance
    placed = []
    for _ in range(cell_count):
        radius = random.randint(*cell_size_range)
        margin = radius + 5
        for attempt in range(50):
            x = random.randint(margin, IMG_SIZE - margin)
            y = random.randint(margin, IMG_SIZE - margin)

            # Check overlap with placed cells
            overlap = False
            for px, py, pr in placed:
                dist = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
                if dist < radius + pr + 5:
                    overlap = True
                    break

            if not overlap:
                placed.append((x, y, radius))
                nucleus_ratio = random.uniform(*nucleus_ratio_range)
                is_blast = random.random() < (blast_pct_range[1] / 100)
                draw_cell(draw, x, y, radius, nucleus_ratio, is_blast)
                break

    # Apply slight blur to make it look more realistic
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    return img


def generate_dataset(output_dir: str, samples_per_class: int = 500):
    """Generate synthetic dataset organized into class subdirectories."""
    print(f"\n{'='*60}")
    print(f"🖼️  Generating {samples_per_class} synthetic images per class...")
    print(f"{'='*60}\n")

    for cls_name in CLASS_LABELS:
        cls_dir = os.path.join(output_dir, cls_name)
        os.makedirs(cls_dir, exist_ok=True)

        pattern = CLASS_PATTERNS[cls_name]
        print(f"  {cls_name}: {pattern['description']}")

        for i in range(samples_per_class):
            img = generate_synthetic_image(cls_name)
            path = os.path.join(cls_dir, f"{cls_name.lower()}_{i+1:04d}.png")
            img.save(path)

            if (i + 1) % 100 == 0:
                print(f"    → {i+1}/{samples_per_class}")

        print(f"  ✅ {cls_name}: {samples_per_class} images saved\n")

    print(f"{'='*60}")
    print(f"✅ Dataset generated: {output_dir}")
    print(f"   Total: {samples_per_class * 3} images")
    print(f"   Structure:")
    for cls_name in CLASS_LABELS:
        print(f"     {output_dir}/{cls_name}/")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic blood cell images")
    parser.add_argument("--output", type=str, default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "images"),
                        help="Output directory for images")
    parser.add_argument("--samples", type=int, default=500, help="Samples per class")
    args = parser.parse_args()

    generate_dataset(args.output, args.samples)


if __name__ == "__main__":
    main()
