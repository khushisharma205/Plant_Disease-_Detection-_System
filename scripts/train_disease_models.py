from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

from config import DISEASE_DATASET_DIR, IMAGE_SIZE, MODELS_DIR

BATCH_SIZE = 32
EPOCHS = 10
PLANTS = {
    'bell_pepper': {'num_classes': 2, 'model_name': 'bell_pepper_disease.keras'},
    'potato': {'num_classes': 3, 'model_name': 'potato_disease.keras'},
    'tomato': {'num_classes': 3, 'model_name': 'tomato_disease.keras'},
}


def build_model(num_classes: int):
    base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(*IMAGE_SIZE, 3))
    base.trainable = False
    model = models.Sequential([
        base,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes, activation='softmax'),
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model


def load_dataset(directory: Path, shuffle: bool):
    return tf.keras.utils.image_dataset_from_directory(
        directory,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='int',
        shuffle=shuffle,
    )


def train_one(plant_key: str, num_classes: int, model_name: str):
    train_dir = DISEASE_DATASET_DIR / plant_key / 'train'
    val_dir = DISEASE_DATASET_DIR / plant_key / 'val'
    if not train_dir.exists() or not val_dir.exists():
        raise FileNotFoundError(f'Missing disease dataset for {plant_key}')

    train_ds = load_dataset(train_dir, True).map(lambda x, y: (x / 255.0, y)).prefetch(tf.data.AUTOTUNE)
    val_ds = load_dataset(val_dir, False).map(lambda x, y: (x / 255.0, y)).prefetch(tf.data.AUTOTUNE)

    class_names = train_ds.class_names if hasattr(train_ds, 'class_names') else None
    print(f'{plant_key} classes: {class_names}')

    model_path = MODELS_DIR / model_name
    model = build_model(num_classes)
    callbacks = [
        EarlyStopping(patience=3, restore_best_weights=True),
        ReduceLROnPlateau(patience=2, factor=0.5),
        ModelCheckpoint(model_path, save_best_only=True),
    ]
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)
    model.save(model_path)
    print(f'Saved {plant_key} disease model to {model_path}')


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for plant_key, cfg in PLANTS.items():
        train_one(plant_key, cfg['num_classes'], cfg['model_name'])


if __name__ == '__main__':
    main()
