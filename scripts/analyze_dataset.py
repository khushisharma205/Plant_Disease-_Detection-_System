import csv
import json
from pathlib import Path

from PIL import Image

from config import PROCESSED_DIR, REPORTS_DIR

VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def image_files(folder: Path):
    return [p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS]


def summarize_folder(folder: Path):
    files = image_files(folder)
    widths = []
    heights = []
    sizes = []
    for file in files:
        try:
            with Image.open(file) as img:
                w, h = img.size
            widths.append(w)
            heights.append(h)
            sizes.append(file.stat().st_size / 1024)
        except Exception:
            continue

    count = len(widths)
    return {
        'folder': str(folder.relative_to(PROCESSED_DIR)),
        'images': count,
        'avg_width': round(sum(widths) / count, 2) if count else 0,
        'avg_height': round(sum(heights) / count, 2) if count else 0,
        'avg_file_size_kb': round(sum(sizes) / count, 2) if count else 0,
    }


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    targets = []
    for folder in sorted(PROCESSED_DIR.rglob('*')):
        if folder.is_dir() and any(child.is_file() for child in folder.rglob('*')):
            targets.append(folder)

    seen = set()
    rows = []
    for folder in targets:
        key = str(folder)
        if key in seen:
            continue
        seen.add(key)
        rows.append(summarize_folder(folder))

    json_path = REPORTS_DIR / 'dataset_summary.json'
    csv_path = REPORTS_DIR / 'dataset_summary.csv'

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2)

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['folder', 'images', 'avg_width', 'avg_height', 'avg_file_size_kb'])
        writer.writeheader()
        writer.writerows(rows)

    print(f'Wrote {json_path}')
    print(f'Wrote {csv_path}')


if __name__ == '__main__':
    main()
