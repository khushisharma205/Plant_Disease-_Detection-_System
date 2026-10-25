import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SCRIPTS = [
    BASE_DIR / 'scripts' / 'prepare_hierarchical_dataset.py',
    BASE_DIR / 'scripts' / 'analyze_dataset.py',
    BASE_DIR / 'scripts' / 'train_plant_classifier.py',
    BASE_DIR / 'scripts' / 'train_disease_models.py',
]


def run(script_path: Path):
    print(f'Running {script_path.name} ...')
    subprocess.run([sys.executable, str(script_path)], check=True)


def main():
    for script in SCRIPTS:
        run(script)
    print('All training steps completed successfully.')


if __name__ == '__main__':
    main()
