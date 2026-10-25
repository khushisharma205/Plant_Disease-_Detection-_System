import os
import sys
import json
from pathlib import Path

DATASET_DIR = Path(r"E:\plantguard-realworld\plantguard-realworld\PlantVillage")
MODELS_DIR  = Path(r"E:\plantguard-realworld\plantguard-realworld\models")
CKPT_DIR    = Path(r"E:\plantguard-realworld\plantguard-realworld\checkpoints")

IMAGE_SIZE     = (224, 224)
BATCH_SIZE     = 64       # tha 32
EPOCHS_PLANT   = 3        # tha 15
EPOCHS_DISEASE = 5        # tha 20
LEARNING_RATE  = 0.001

print("Libraries load ho rahi hain...")
import numpy as np

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.callbacks import (
        EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
    )
    print(f"TensorFlow version: {tf.__version__}")
except ImportError:
    print("\nERROR: TensorFlow install nahi hai!")
    print("Run karo: pip install tensorflow")
    sys.exit(1)

try:
    tf.keras.mixed_precision.set_global_policy('mixed_float16')
    print("Mixed precision ON - training fast hogi!")
except Exception as e:
    print(f"Mixed precision skip: {e}")

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"GPU mila: {gpus[0].name}")
    tf.config.experimental.set_memory_growth(gpus[0], True)
else:
    print("GPU nahi mila, CPU pe chalega")


def detect_folders(dataset_dir: Path):
    train_dir = dataset_dir / "train"
    if not train_dir.exists():
        print(f"ERROR: train folder nahi mila: {train_dir}")
        sys.exit(1)

    folder_map = {}

    for folder in sorted(train_dir.iterdir()):
        if not folder.is_dir():
            continue

        name = folder.name
        name_lower = name.lower()

        if name_lower.startswith("tomato"):
            plant = "tomato"
        elif name_lower.startswith("potato"):
            plant = "potato"
        elif name_lower.startswith("pepper"):
            plant = "bell_pepper"
        else:
            print(f"  SKIP (unknown): {name}")
            continue

        name_clean = name_lower.replace("_", " ").replace(",", "").strip()

        if "bacterial spot" in name_clean:
            disease = "bacterial_spot"
        elif "early blight" in name_clean:
            disease = "early_blight"
        elif "late blight" in name_clean:
            disease = "late_blight"
        elif "healthy" in name_clean:
            disease = "healthy"
        else:
            print(f"  SKIP (unknown disease): {name}")
            continue

        folder_map[name] = (plant, disease)
        print(f"  OK  {name}")
        print(f"      -> plant={plant}, disease={disease}")

    return folder_map


def find_folder_in_split(split_dir: Path, folder_name: str) -> Path:
    exact = split_dir / folder_name
    if exact.exists():
        return exact

    target = folder_name.lower().replace("_", "").replace(",", "").replace(" ", "")
    for f in split_dir.iterdir():
        if not f.is_dir():
            continue
        candidate = f.name.lower().replace("_", "").replace(",", "").replace(" ", "")
        if candidate == target:
            return f
    return None


PLANT_CLASSES = ["bell_pepper", "potato", "tomato"]

DISEASE_CLASSES = {
    "tomato":      ["bacterial_spot", "early_blight", "healthy", "late_blight"],
    "potato":      ["early_blight", "healthy", "late_blight"],
    "bell_pepper": ["bacterial_spot", "healthy"],
}


def save_class_names(model_name, class_names):
    path = MODELS_DIR / f"{model_name}_classes.json"
    with open(path, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"  Class names saved: {path.name}")


def load_dataset_for_plant(split: str, folder_map: dict, plant_filter=None):
    split_dir = DATASET_DIR / split
    if not split_dir.exists():
        print(f"ERROR: {split} directory nahi mili: {split_dir}")
        sys.exit(1)

    images = []
    labels = []

    if plant_filter is None:
        class_names = PLANT_CLASSES
        label_map   = {p: i for i, p in enumerate(PLANT_CLASSES)}

        for folder_name, (plant, _) in folder_map.items():
            folder_path = find_folder_in_split(split_dir, folder_name)
            if folder_path is None:
                print(f"  WARN: {split}/{folder_name} nahi mila, skip")
                continue
            label_idx = label_map[plant]
            for ext in ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG", "*.png", "*.PNG"):
                for img in folder_path.glob(ext):
                    images.append(str(img))
                    labels.append(label_idx)
    else:
        class_names = DISEASE_CLASSES[plant_filter]
        label_map   = {d: i for i, d in enumerate(class_names)}

        for folder_name, (plant, disease) in folder_map.items():
            if plant != plant_filter:
                continue
            folder_path = find_folder_in_split(split_dir, folder_name)
            if folder_path is None:
                print(f"  WARN: {split}/{folder_name} nahi mila, skip")
                continue
            label_idx = label_map[disease]
            for ext in ("*.jpg", "*.JPG", "*.jpeg", "*.JPEG", "*.png", "*.PNG"):
                for img in folder_path.glob(ext):
                    images.append(str(img))
                    labels.append(label_idx)

    if len(images) == 0:
        print(f"  ERROR: {split} mein koi image nahi mili!")
    else:
        print(f"  {split}: {len(images)} images | {len(class_names)} classes: {class_names}")

    return images, labels, class_names


def create_tf_dataset(image_paths, labels, num_classes, is_training=True):
    def load_and_preprocess(path, label):
        img = tf.io.read_file(path)
        img = tf.image.decode_image(img, channels=3, expand_animations=False)
        img.set_shape([None, None, 3])
        img = tf.image.resize(img, IMAGE_SIZE)
        img = tf.cast(img, tf.float32) / 255.0
        return img, tf.one_hot(label, num_classes)

    def augment(img, label):
        img = tf.image.random_flip_left_right(img)
        img = tf.image.random_flip_up_down(img)
        img = tf.image.random_brightness(img, 0.2)
        img = tf.image.random_contrast(img, 0.8, 1.2)
        img = tf.image.random_saturation(img, 0.8, 1.2)
        img = tf.clip_by_value(img, 0.0, 1.0)
        return img, label

    ds = tf.data.Dataset.from_tensor_slices((image_paths, labels))
    ds = ds.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    if is_training:
        ds = ds.shuffle(2000).map(augment, num_parallel_calls=tf.data.AUTOTUNE)
    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


def build_model(num_classes, model_name):
    print(f"  Model build: {model_name} | {num_classes} classes")
    base = MobileNetV2(input_shape=(*IMAGE_SIZE, 3), include_top=False, weights='imagenet')
    base.trainable = False

    inputs  = keras.Input(shape=(*IMAGE_SIZE, 3))
    x       = base(inputs, training=False)
    x       = layers.GlobalAveragePooling2D()(x)
    x       = layers.BatchNormalization()(x)
    x       = layers.Dense(256, activation='relu')(x)
    x       = layers.Dropout(0.4)(x)
    x       = layers.Dense(128, activation='relu')(x)
    x       = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax', dtype='float32')(x)

    model = keras.Model(inputs, outputs, name=model_name)
    model.compile(
        optimizer=keras.optimizers.Adam(LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model, base


def train_model(plant_filter, model_name, save_path, epochs, folder_map):
    label = "Plant Classifier" if plant_filter is None else f"{plant_filter.title()} Disease"
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")

    ckpt_path = CKPT_DIR / f"{model_name}_ckpt.keras"

    print("Data load ho raha hai...")
    train_paths, train_labels, class_names = load_dataset_for_plant('train', folder_map, plant_filter)
    val_paths,   val_labels,   _           = load_dataset_for_plant('val',   folder_map, plant_filter)

    if len(train_paths) == 0:
        print("  Koi data nahi mila! Skip.")
        return 0.0

    num_classes = len(class_names)
    train_ds = create_tf_dataset(train_paths, train_labels, num_classes, is_training=True)
    val_ds   = create_tf_dataset(val_paths,   val_labels,   num_classes, is_training=False)

    if ckpt_path.exists():
        print(f"  Checkpoint mila! Resume ho raha hai: {ckpt_path.name}")
        model = keras.models.load_model(str(ckpt_path))
        base_model = next((l for l in model.layers if 'mobilenetv2' in l.name.lower()), None)
    else:
        print("  Fresh start...")
        model, base_model = build_model(num_classes, model_name)

    def get_callbacks():
        return [
            EarlyStopping(patience=3, restore_best_weights=True, verbose=1),  # tha 5
            ReduceLROnPlateau(factor=0.5, patience=2, verbose=1, min_lr=1e-7),  # tha 3
            ModelCheckpoint(
                filepath=str(ckpt_path),
                save_best_only=True,
                monitor='val_accuracy',
                verbose=1
            ),
        ]

    print("\nPhase 1: Feature Extraction...")
    history = model.fit(train_ds, validation_data=val_ds,
                        epochs=epochs, callbacks=get_callbacks(), verbose=1)
    print(f"Phase 1 best: {max(history.history['val_accuracy'])*100:.1f}%")

    print("\nPhase 2: Fine-tuning...")
    if base_model is not None:
        base_model.trainable = True
        for layer in base_model.layers[:-30]:
            layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(LEARNING_RATE / 10),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    model.fit(train_ds, validation_data=val_ds,
              epochs=3, callbacks=get_callbacks(), verbose=1)   # tha 10

    model.save(str(save_path))
    save_class_names(model_name, class_names)
    print(f"  Saved: {save_path.name}")

    loss, acc = model.evaluate(val_ds, verbose=0)
    print(f"  Final Accuracy: {acc*100:.1f}%  |  Loss: {loss:.4f}")
    return acc


def main():
    print("\n" + "="*55)
    print("  PlantGuard AI - Training (AUTO FOLDER DETECT)")
    print("="*55)

    if not DATASET_DIR.exists():
        print(f"ERROR: Dataset nahi mila: {DATASET_DIR}")
        sys.exit(1)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    CKPT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nDataset : {DATASET_DIR}")
    print(f"Models  : {MODELS_DIR}")
    print(f"Checkpts: {CKPT_DIR}")

    print("\nFolders auto-detect ho rahe hain...")
    folder_map = detect_folders(DATASET_DIR)
    print(f"\nTotal {len(folder_map)} folders detect hue\n")

    if len(folder_map) == 0:
        print("ERROR: Koi folder nahi mila! Dataset path check karo.")
        sys.exit(1)

    results = {}

    results['plant_classifier'] = train_model(
        plant_filter=None,
        model_name="plant_classifier",
        save_path=MODELS_DIR / "plant_classifier.keras",
        epochs=EPOCHS_PLANT,
        folder_map=folder_map,
    )

    results['tomato_disease'] = train_model(
        plant_filter="tomato",
        model_name="tomato_disease",
        save_path=MODELS_DIR / "tomato_disease.keras",
        epochs=EPOCHS_DISEASE,
        folder_map=folder_map,
    )

    results['potato_disease'] = train_model(
        plant_filter="potato",
        model_name="potato_disease",
        save_path=MODELS_DIR / "potato_disease.keras",
        epochs=EPOCHS_DISEASE,
        folder_map=folder_map,
    )

    results['bell_pepper_disease'] = train_model(
        plant_filter="bell_pepper",
        model_name="bell_pepper_disease",
        save_path=MODELS_DIR / "bell_pepper_disease.keras",
        epochs=EPOCHS_DISEASE,
        folder_map=folder_map,
    )

    print("\n" + "="*55)
    print("  TRAINING COMPLETE!")
    print("="*55)
    for name, acc in results.items():
        status = "GOOD" if acc > 0.85 else "CHECK - accuracy low hai"
        print(f"  {name:25s}: {acc*100:.1f}%  [{status}]")

    print(f"\nModels: {MODELS_DIR.absolute()}")
    print("Ab app.py run karo!")


if __name__ == "__main__":
    main()