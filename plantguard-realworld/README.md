RUNNING PROCESS:----
cd D:\plantguard-realworld\plantguard-realworld
python app.pycd

# PlantGuard AI - Real World Project Version

Ye project 3-plant hierarchical plant disease detection system hai.

## Covered plants
- Tomato
- Potato
- Bell Pepper

## Covered classes
- Tomato: Healthy, Early Blight, Late Blight
- Potato: Healthy, Early Blight, Late Blight
- Bell Pepper: Healthy, Bacterial Spot

## Project flow
1. User image upload karta hai
2. Plant classifier plant detect karta hai
3. Us plant ke liye disease-specific model run hota hai
4. Symptoms + prevention UI me dikhte hain
5. Prediction SQLite database me save hoti hai

## Folder structure
- `app.py` - Flask app
- `config.py` - central paths and label mapping
- `database.py` - SQLite logic
- `model_service.py` - demo/trained inference logic
- `knowledge_base.py` - symptoms and prevention text
- `templates/` - HTML pages
- `static/` - CSS, JS, uploads
- `scripts/prepare_hierarchical_dataset.py` - raw dataset se split + hierarchical dataset ready karta hai
- `scripts/analyze_dataset.py` - processed dataset summary JSON/CSV banata hai
- `scripts/train_plant_classifier.py` - plant model train karta hai
- `scripts/train_disease_models.py` - disease models train karta hai
- `scripts/train_all.py` - sab steps ek saath chalata hai

## Raw dataset folders required
In 8 folders ko `data/raw_dataset/` ke andar directly rakho:
- `Tomato___healthy`
- `Tomato___Early_blight`
- `Tomato___Late_blight`
- `Potato___healthy`
- `Potato___Early_blight`
- `Potato___Late_blight`
- `Pepper__bell___healthy`
- `Pepper__bell___Bacterial_spot`

## Setup
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
```

## Prepare + train
```bash
python scripts/prepare_hierarchical_dataset.py
python scripts/analyze_dataset.py
python scripts/train_plant_classifier.py
python scripts/train_disease_models.py
```

Ya ek command:
```bash
python scripts/train_all.py
```

## Run app
```bash
python app.py
```
Open: `http://127.0.0.1:5000`

## Modes
- Demo mode: agar trained models available nahi hain
- Trained mode: jab `models/` folder me `.keras` files saved hon

## Important improvements over original folder
- Hardcoded Windows dataset path remove kar diya gaya hai
- Broken extra folders clean kar diye gaye hain
- Real raw-to-processed dataset pipeline add ki gayi hai
- Training scripts split kiye gaye hain
- Secure upload handling add ki gayi hai
- Model loading cached kiya gaya hai
- DB path and folders centralized kar diye gaye hain
