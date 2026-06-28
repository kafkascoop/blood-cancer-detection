"""
Generate synthetic blood smear images for CNN training.

Creates image samples that visually correspond to four classes
(Normal, Leukemia, Lymphoma, Myeloma) using class-specific medical patterns.

Each class has distinctive visual characteristics:
  - Normal:  Small uniform cells, small round nuclei, even distribution, light pink stain
  - Leukemia: Very large irregular blast cells, huge dark nuclei, sparse, dark purple stain
  - Lymphoma: Clumped/aggregated lymphocytes, medium size, irregular shapes, darker margins
  - Myeloma:  Plasma cells with eccentric (off-center) nuclei, some binucleated, slightly larger

Usage:
    python -m app.ml.generate_synthetic_images --output ./data/images --samples 500
"""
import os
import random
import argparse
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

random.seed(42)
np.random.seed(42)

IMG_SIZE = 224
CLASS_LABELS = ["Normal", "Leukemia", "Lymphoma", "Myeloma"]

CLASS_PATTERNS = {
    "Normal": {
        "cell_count_range": (18, 28),
        "cell_size_range": (7, 13),
        "nucleus_ratio_range": (0.25, 0.33),
        "nucleus_eccentricity": (0.5, 0.6),  # 0=centered, 1=very eccentric
        "cytoplasm_color": ((220, 200, 225), (240, 220, 245)),  # light pink/purple
        "nucleus_color": ((70, 50, 110), (100, 75, 140)),       # medium purple
        "cluster_prob": 0.05,      # low clustering
        "binucleated_pct": (0, 3),  # rare
        "description": "Healthy cells: uniform size, round nuclei, even distribution",
    },
    "Leukemia": {
        "cell_count_range": (4, 10),
        "cell_size_range": (20, 35),
        "nucleus_ratio_range": (0.55, 0.75),
        "nucleus_eccentricity": (0.55, 0.70),
        "cytoplasm_color": ((190, 170, 205), (220, 195, 225)),
        "nucleus_color": ((35, 20, 85), (60, 40, 110)),
        "cluster_prob": 0.10,
        "binucleated_pct": (3, 10),
        "description": "Leukemia: large blast cells, huge dark irregular nuclei, sparse",
    },
    "Lymphoma": {
        "cell_count_range": (10, 16),
        "cell_size_range": (14, 22),
        "nucleus_ratio_range": (0.42, 0.58),
        "nucleus_eccentricity": (0.55, 0.75),
        "cytoplasm_color": ((200, 180, 215), (230, 210, 240)),
        "nucleus_color": ((55, 35, 95), (85, 60, 125)),
        "cluster_prob": 0.45,       # high clustering (hallmark of lymphoma)
        "binucleated_pct": (2, 8),
        "description": "Lymphoma: clumped atypical lymphocytes, irregular shapes",
    },
    "Myeloma": {
        "cell_count_range": (14, 22),
        "cell_size_range": (12, 18),
        "nucleus_ratio_range": (0.35, 0.48),
        "nucleus_eccentricity": (0.70, 0.88),  # highly eccentric (plasma cells)
        "cytoplasm_color": ((200, 195, 220), (235, 225, 245)),
        "nucleus_color": ((60, 45, 100), (90, 70, 130)),
        "cluster_prob": 0.15,
        "binucleated_pct": (5, 15),  # higher binucleation (myeloma hallmark)
        "description": "Myeloma: plasma cells with eccentric nuclei, binucleation",
    },
}


def draw_cell(draw, x, y, radius, nucleus_ratio, nucleus_eccentricity,
              cyto_color_range, nuc_color_range, is_binucleated=False):
    """Draw a single blood cell with nucleus at position (x, y)."""
    # --- Cytoplasm (cell body) ---
    cyto_r = random.randint(cyto_color_range[0][0], cyto_color_range[1][0])
    cyto_g = random.randint(cyto_color_range[0][1], cyto_color_range[1][1])
    cyto_b = random.randint(cyto_color_range[0][2], cyto_color_range[1][2])
    cyto_color = (cyto_r, cyto_g, cyto_b)

    # Slight irregular shape for cancer cells
    if nucleus_ratio > 0.45:
        # Non-uniform shape
        rx = radius * random.uniform(0.85, 1.0)
        ry = radius * random.uniform(0.95, 1.15)
        x1, y1 = x - rx, y - ry
        x2, y2 = x + rx, y + ry
        draw.ellipse([x1, y1, x2, y2], fill=cyto_color, outline=None)
    else:
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=cyto_color, outline=None
        )

    # --- Nucleus ---
    nucleus_radius = int(radius * nucleus_ratio)
    nuc_r = random.randint(nuc_color_range[0][0], nuc_color_range[1][0])
    nuc_g = random.randint(nuc_color_range[0][1], nuc_color_range[1][1])
    nuc_b = random.randint(nuc_color_range[0][2], nuc_color_range[1][2])
    nuc_color = (nuc_r, nuc_g, nuc_b)

    if is_binucleated:
        # Two nuclei (hallmark of myeloma / some lymphomas)
        offset = nucleus_radius // 2
        for dx in [-offset, offset]:
            draw.ellipse(
                [
                    x + dx - nucleus_radius // 2,
                    y - nucleus_radius // 2,
                    x + dx + nucleus_radius // 2,
                    y + nucleus_radius // 2,
                ],
                fill=nuc_color,
            )
    else:
        # Single nucleus with eccentricity (offset from center)
        ecc_offset = int(nucleus_radius * (nucleus_eccentricity - 0.5) * 0.8)
        nx = x + ecc_offset
        ny = y + random.randint(-3, 3)

        # Irregular nucleus shape for blast cells
        if nucleus_ratio > 0.5:
            # Often irregular in shape
            nuc_x_radius = nucleus_radius * random.uniform(0.85, 1.15)
            nuc_y_radius = nucleus_radius * random.uniform(0.90, 1.10)
            draw.ellipse(
                [nx - nuc_x_radius, ny - nuc_y_radius,
                 nx + nuc_x_radius, ny + nuc_y_radius],
                fill=nuc_color,
            )
        else:
            draw.ellipse(
                [nx - nucleus_radius, ny - nucleus_radius,
                 nx + nucleus_radius, ny + nucleus_radius],
                fill=nuc_color,
            )

    # --- Nucleolus (small darker dot inside nucleus) ---
    if random.random() < 0.6:
        nux = x + random.randint(-nucleus_radius // 3, nucleus_radius // 3)
        nuy = y + random.randint(-nucleus_radius // 3, nucleus_radius // 3)
        dot_r = random.randint(1, max(2, nucleus_radius // 5))
        draw.ellipse(
            [nux - dot_r, nuy - dot_r, nux + dot_r, nuy + dot_r],
            fill=(max(0, nuc_r - 30), max(0, nuc_g - 25), max(0, nuc_b - 35)),
        )


def generate_synthetic_image(cls_name: str) -> Image.Image:
    """Generate a synthetic blood smear image for the given class."""
    # Background: light pink-gray for Normal, slightly different for others
    if cls_name == "Normal":
        bg = (248, 242, 250)
    elif cls_name == "Leukemia":
        bg = (240, 235, 245)
    elif cls_name == "Lymphoma":
        bg = (242, 236, 248)
    else:  # Myeloma
        bg = (244, 240, 248)

    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), bg)
    draw = ImageDraw.Draw(img)

    pattern = CLASS_PATTERNS[cls_name]

    cell_count = random.randint(*pattern["cell_count_range"])
    cell_size_range = pattern["cell_size_range"]
    nucleus_ratio_range = pattern["nucleus_ratio_range"]
    eccentricity_range = pattern["nucleus_eccentricity"]
    cyto_color_range = pattern["cytoplasm_color"]
    nuc_color_range = pattern["nucleus_color"]
    cluster_prob = pattern["cluster_prob"]
    binucleated_pct = pattern["binucleated_pct"]

    # --- Background texture (fine noise + some staining artifacts) ---
    noise = Image.new("RGB", (IMG_SIZE, IMG_SIZE), bg)
    noise_pixels = noise.load()
    for _ in range(800):
        nx = random.randint(0, IMG_SIZE - 1)
        ny = random.randint(0, IMG_SIZE - 1)
        offset = random.randint(-12, 12)
        r = max(0, min(255, bg[0] + offset))
        g = max(0, min(255, bg[1] + offset))
        b = max(0, min(255, bg[2] + offset // 2))
        noise_pixels[nx, ny] = (r, g, b)

    # Add some small staining debris (tiny dots)
    for _ in range(random.randint(5, 15)):
        dx = random.randint(10, IMG_SIZE - 10)
        dy = random.randint(10, IMG_SIZE - 10)
        ds = random.randint(1, 3)
        dc = random.randint(180, 210)
        draw.ellipse(
            [dx - ds, dy - ds, dx + ds, dy + ds],
            fill=(dc, dc - 10, dc + 15),
        )

    img.paste(noise, (0, 0), mask=None)

    # --- Place cells ---
    placed = []

    # For lymphoma, create clusters of cells close together
    create_clusters = random.random() < cluster_prob

    if create_clusters and cls_name == "Lymphoma":
        # Create 2-4 clusters of aggregated lymphocytes
        num_clusters = random.randint(2, 4)
        cluster_centers = []
        for _ in range(num_clusters):
            cx = random.randint(40, IMG_SIZE - 40)
            cy = random.randint(40, IMG_SIZE - 40)
            cluster_centers.append((cx, cy))

        for cell_i in range(cell_count):
            cluster_cx, cluster_cy = random.choice(cluster_centers)
            radius = random.randint(*cell_size_range)
            for attempt in range(30):
                offset_angle = random.uniform(0, 2 * math.pi)
                offset_dist = random.uniform(2, radius * 2.5)
                x = int(cluster_cx + offset_dist * math.cos(offset_angle))
                y = int(cluster_cy + offset_dist * math.sin(offset_angle))
                if not (radius + 5 < x < IMG_SIZE - radius - 5 and
                        radius + 5 < y < IMG_SIZE - radius - 5):
                    continue
                overlap = any(
                    ((x - px) ** 2 + (y - py) ** 2) ** 0.5 < radius + pr + 3
                    for px, pr, py in placed
                )
                if not overlap:
                    placed.append((x, y, radius))
                    nucleus_ratio = random.uniform(*nucleus_ratio_range)
                    eccentricity = random.uniform(*eccentricity_range)
                    is_binuc = random.random() < (binucleated_pct[1] / 100)
                    draw_cell(draw, x, y, radius, nucleus_ratio, eccentricity,
                              cyto_color_range, nuc_color_range, is_binuc)
                    break
    elif create_clusters:
        # General clustering (not just lymphoma)
        num_clusters = random.randint(1, 3)
        cluster_centers = []
        for _ in range(num_clusters):
            cx = random.randint(40, IMG_SIZE - 40)
            cy = random.randint(40, IMG_SIZE - 40)
            cluster_centers.append((cx, cy))

        for cell_i in range(cell_count):
            cluster_cx, cluster_cy = random.choice(cluster_centers)
            radius = random.randint(*cell_size_range)
            offset_angle = random.uniform(0, 2 * math.pi)
            offset_dist = random.uniform(2, radius * 3)
            x = int(cluster_cx + offset_dist * math.cos(offset_angle))
            y = int(cluster_cy + offset_dist * math.sin(offset_angle))
            if not (radius + 5 < x < IMG_SIZE - radius - 5 and
                    radius + 5 < y < IMG_SIZE - radius - 5):
                continue
            overlap = any(
                ((x - px) ** 2 + (y - py) ** 2) ** 0.5 < radius + pr + 3
                for px, pr, py in placed
            )
            if not overlap:
                placed.append((x, y, radius))
                nucleus_ratio = random.uniform(*nucleus_ratio_range)
                eccentricity = random.uniform(*eccentricity_range)
                is_binuc = random.random() < (binucleated_pct[1] / 100)
                draw_cell(draw, x, y, radius, nucleus_ratio, eccentricity,
                          cyto_color_range, nuc_color_range, is_binuc)
    else:
        # Even distribution
        for _ in range(cell_count):
            radius = random.randint(*cell_size_range)
            margin = radius + 5
            for attempt in range(100):
                x = random.randint(margin, IMG_SIZE - margin)
                y = random.randint(margin, IMG_SIZE - margin)
                overlap = any(
                    ((x - px) ** 2 + (y - py) ** 2) ** 0.5 < radius + pr + 5
                    for px, pr, py in placed
                )
                if not overlap:
                    placed.append((x, y, radius))
                    nucleus_ratio = random.uniform(*nucleus_ratio_range)
                    eccentricity = random.uniform(*eccentricity_range)
                    is_binuc = random.random() < (binucleated_pct[1] / 100)
                    draw_cell(draw, x, y, radius, nucleus_ratio, eccentricity,
                              cyto_color_range, nuc_color_range, is_binuc)
                    break

    # For leukemia: add some extra staining artifacts (dark purple spots)
    if cls_name == "Leukemia":
        for _ in range(random.randint(3, 8)):
            ax = random.randint(20, IMG_SIZE - 20)
            ay = random.randint(20, IMG_SIZE - 20)
            ar = random.randint(1, 3)
            draw.ellipse(
                [ax - ar, ay - ar, ax + ar, ay + ar],
                fill=(random.randint(40, 80), random.randint(20, 50), random.randint(80, 120)),
            )

    # Apply very slight blur to soften edges
    img = img.filter(ImageFilter.GaussianBlur(radius=0.4))
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
    print(f"   Total: {samples_per_class * len(CLASS_LABELS)} images")
    print(f"   Structure:")
    for cls_name in CLASS_LABELS:
        print(f"     {output_dir}/{cls_name}/")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic blood cell images")
    parser.add_argument("--output", type=str,
                        default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                             "data", "images"),
                        help="Output directory for images")
    parser.add_argument("--samples", type=int, default=500, help="Samples per class")
    args = parser.parse_args()

    generate_dataset(args.output, args.samples)


if __name__ == "__main__":
    main()
