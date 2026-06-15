import random
import shutil
from pathlib import Path

from config import RAW_CLASS_MAP, RAW_DATASET_DIR, PLANT_DATASET_DIR, DISEASE_DATASET_DIR

SPLITS = {'train': 0.70, 'val': 0.15, 'test': 0.15}
SEED = 42
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def collect_images(folder: Path):
    return sorted([p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS])


def split_items(items):
    random.Random(SEED).shuffle(items)
    total = len(items)
    train_end = int(total * SPLITS['train'])
    val_end = train_end + int(total * SPLITS['val'])
    return {
        'train': items[:train_end],
        'val': items[train_end:val_end],
        'test': items[val_end:],
    }


def ensure_clean_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main():
    missing = [name for name in RAW_CLASS_MAP if not (RAW_DATASET_DIR / name).exists()]
    if missing:
        print('Missing raw dataset folders:')
        for name in missing:
            print(f' - {name}')
        raise SystemExit(1)

    ensure_clean_dir(PLANT_DATASET_DIR)
    ensure_clean_dir(DISEASE_DATASET_DIR)

    summary = []
    for raw_folder_name, (plant_key, disease_key) in RAW_CLASS_MAP.items():
        folder = RAW_DATASET_DIR / raw_folder_name
        images = collect_images(folder)
        if not images:
            print(f'Skipping empty folder: {raw_folder_name}')
            continue

        split_map = split_items(images)
        for split_name, paths in split_map.items():
            for image_path in paths:
                plant_dst = PLANT_DATASET_DIR / split_name / plant_key / image_path.name
                disease_dst = DISEASE_DATASET_DIR / plant_key / split_name / disease_key / image_path.name
                copy_file(image_path, plant_dst)
                copy_file(image_path, disease_dst)

        summary.append((raw_folder_name, plant_key, disease_key, len(images)))

    print('Hierarchical dataset prepared successfully.')
    for raw_folder_name, plant_key, disease_key, count in summary:
        print(f'{raw_folder_name} -> plant={plant_key}, disease={disease_key}, images={count}')
    print(f'Plant classifier dataset: {PLANT_DATASET_DIR}')
    print(f'Disease datasets: {DISEASE_DATASET_DIR}')


if __name__ == '__main__':
    main()
