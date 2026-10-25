from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATASET_DIR = DATA_DIR / 'raw_dataset'
PROCESSED_DIR = DATA_DIR / 'processed'
PLANT_DATASET_DIR = PROCESSED_DIR / 'plant_classifier'
DISEASE_DATASET_DIR = PROCESSED_DIR / 'disease'
MODELS_DIR = BASE_DIR / 'models'
REPORTS_DIR = BASE_DIR / 'reports'
INSTANCE_DIR = BASE_DIR / 'instance'
STATIC_DIR = BASE_DIR / 'static'
UPLOAD_DIR = STATIC_DIR / 'uploads'
DB_PATH = INSTANCE_DIR / 'plant_disease.db'

IMAGE_SIZE = (224, 224)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

PLANT_DISPLAY = {
    'bell_pepper': 'Bell Pepper',
    'potato':      'Potato',
    'tomato':      'Tomato',
}

DISEASE_DISPLAY = {
    'bell_pepper': {
        'bacterial_spot': 'Bacterial Spot',
        'healthy':        'Healthy',
    },
    'potato': {
        'early_blight': 'Early Blight',
        'healthy':      'Healthy',
        'late_blight':  'Late Blight',
    },
    'tomato': {
        'bacterial_spot': 'Bacterial Spot',  # FIX: missing tha
        'early_blight':   'Early Blight',
        'healthy':        'Healthy',
        'late_blight':    'Late Blight',
    },
}

RAW_CLASS_MAP = {
    'Tomato__healthy':            ('tomato', 'healthy'),
    'Tomato__Early_blight':       ('tomato', 'early_blight'),
    'Tomato__Late_blight':        ('tomato', 'late_blight'),
    'Tomato__Bacterial_spot':     ('tomato', 'bacterial_spot'),  # FIX: missing tha

    'Potato__healthy':            ('potato', 'healthy'),
    'Potato__Early_blight':       ('potato', 'early_blight'),
    'Potato__Late_blight':        ('potato', 'late_blight'),

    'Pepper,_bell__healthy':          ('bell_pepper', 'healthy'),
    'Pepper,_bell__Bacterial_spot':   ('bell_pepper', 'bacterial_spot'),
}

for folder in [DATA_DIR, RAW_DATASET_DIR, PROCESSED_DIR, MODELS_DIR,
               REPORTS_DIR, INSTANCE_DIR, STATIC_DIR, UPLOAD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)