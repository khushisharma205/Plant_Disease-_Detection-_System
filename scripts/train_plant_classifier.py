from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

from config import IMAGE_SIZE, MODELS_DIR, PLANT_DATASET_DIR

BATCH_SIZE = 32
EPOCHS = 10
MODEL_PATH = MODELS_DIR / 'plant_classifier.keras'


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


def load_dataset(split: str, shuffle: bool):
    directory = PLANT_DATASET_DIR / split
    if not directory.exists():
        raise FileNotFoundError(f'Missing dataset directory: {directory}')
    return tf.keras.utils.image_dataset_from_directory(
        directory,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode='int',
        shuffle=shuffle,
    )


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    train_ds = load_dataset('train', True).map(lambda x, y: (x / 255.0, y)).prefetch(tf.data.AUTOTUNE)
    val_ds = load_dataset('val', False).map(lambda x, y: (x / 255.0, y)).prefetch(tf.data.AUTOTUNE)

    class_names = train_ds.class_names if hasattr(train_ds, 'class_names') else None
    print(f'Plant classes: {class_names}')

    model = build_model(num_classes=3)
    callbacks = [
        EarlyStopping(patience=3, restore_best_weights=True),
        ReduceLROnPlateau(patience=2, factor=0.5),
        ModelCheckpoint(MODEL_PATH, save_best_only=True),
    ]

    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)
    model.save(MODEL_PATH)
    print(f'Saved plant classifier to {MODEL_PATH}')


if __name__ == '__main__':
    main()
