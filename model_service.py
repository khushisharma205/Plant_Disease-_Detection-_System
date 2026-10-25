from functools import lru_cache
from pathlib import Path
import json
import random

import numpy as np
from PIL import Image

from config import IMAGE_SIZE, MODELS_DIR, PLANT_DISPLAY, DISEASE_DISPLAY

PLANT_MODEL_PATH = MODELS_DIR / 'plant_classifier.keras'
DISEASE_MODEL_PATHS = {
    'bell_pepper': MODELS_DIR / 'bell_pepper_disease.keras',
    'potato':      MODELS_DIR / 'potato_disease.keras',
    'tomato':      MODELS_DIR / 'tomato_disease.keras',
}

# Fallback class names (agar JSON na mile)
PLANT_CLASS_NAMES = ['bell_pepper', 'potato', 'tomato']
DISEASE_CLASS_NAMES = {
    'bell_pepper': ['bacterial_spot', 'healthy'],
    'potato':      ['early_blight', 'healthy', 'late_blight'],
    'tomato':      ['bacterial_spot', 'early_blight', 'healthy', 'late_blight'],  # FIX: bacterial_spot add
}


def _load_class_names_from_json(model_name: str, fallback: list) -> list:
    json_path = MODELS_DIR / f'{model_name}_classes.json'
    if json_path.exists():
        try:
            with open(json_path) as f:
                names = json.load(f)
            print(f'  Class names loaded: {json_path.name} -> {names}')
            return names
        except Exception as e:
            print(f'  WARN: {json_path.name} read nahi hua ({e}), fallback use ho raha hai')
    else:
        print(f'  WARN: {json_path.name} nahi mila, fallback use ho raha hai')
    return fallback


def _init_class_names():
    plant_names = _load_class_names_from_json('plant_classifier', PLANT_CLASS_NAMES)
    disease_names = {}
    for plant_key, fallback in DISEASE_CLASS_NAMES.items():
        disease_names[plant_key] = _load_class_names_from_json(f'{plant_key}_disease', fallback)
    return plant_names, disease_names


_PLANT_CLASS_NAMES, _DISEASE_CLASS_NAMES = _init_class_names()


def models_ready() -> bool:
    return PLANT_MODEL_PATH.exists() and all(
        p.exists() for p in DISEASE_MODEL_PATHS.values()
    )


@lru_cache(maxsize=1)
def _load_plant_model():
    from tensorflow.keras.models import load_model
    return load_model(PLANT_MODEL_PATH)


@lru_cache(maxsize=3)
def _load_disease_model(plant_key: str):
    from tensorflow.keras.models import load_model
    return load_model(DISEASE_MODEL_PATHS[plant_key])


def _prepare_image(image_path: str) -> np.ndarray:
    img = Image.open(image_path).convert('RGB').resize(IMAGE_SIZE)
    arr = np.asarray(img, dtype='float32') / 255.0
    return np.expand_dims(arr, axis=0)


def _format_prediction(plant_key, disease_key, plant_confidence, disease_confidence, mode) -> dict:
    return {
        'plant':              PLANT_DISPLAY[plant_key],
        'disease':            DISEASE_DISPLAY[plant_key][disease_key],
        'plant_confidence':   round(plant_confidence, 1),
        'disease_confidence': round(disease_confidence, 1),
        'is_healthy':         disease_key == 'healthy',
        'mode':               mode,
    }


def predict_demo(_image_path: str) -> dict:
    plant_key   = random.choice(_PLANT_CLASS_NAMES)
    disease_key = random.choice(_DISEASE_CLASS_NAMES[plant_key])
    return _format_prediction(
        plant_key, disease_key,
        random.uniform(82, 97),
        random.uniform(78, 96),
        'demo',
    )


def predict_trained(image_path: str) -> dict:
    image_batch = _prepare_image(image_path)

    plant_probs      = _load_plant_model().predict(image_batch, verbose=0)[0]
    plant_index      = int(np.argmax(plant_probs))
    plant_key        = _PLANT_CLASS_NAMES[plant_index]
    plant_confidence = float(plant_probs[plant_index] * 100)

    disease_probs      = _load_disease_model(plant_key).predict(image_batch, verbose=0)[0]
    disease_index      = int(np.argmax(disease_probs))
    disease_key        = _DISEASE_CLASS_NAMES[plant_key][disease_index]
    disease_confidence = float(disease_probs[disease_index] * 100)

    return _format_prediction(plant_key, disease_key, plant_confidence, disease_confidence, 'trained')


def predict_image(image_path: str) -> dict:
    if not models_ready():
        return predict_demo(image_path)
    try:
        return predict_trained(image_path)
    except Exception as exc:
        print(f'Model inference failed, falling back to demo mode: {exc}')
        return predict_demo(image_path)