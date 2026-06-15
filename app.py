from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, send_from_directory
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH, UPLOAD_DIR
from database import get_history, get_stats, init_db, save_prediction, delete_prediction
from knowledge_base import get_disease_info
from model_service import predict_image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)

init_db()


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/predict', methods=['POST'])
def predict():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file uploaded'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PNG, JPG, JPEG and WEBP files are allowed'}), 400

    ext = Path(secure_filename(file.filename)).suffix.lower()
    final_name = f'{uuid4().hex}{ext}'
    file_path = UPLOAD_DIR / final_name
    file.save(file_path)

    try:
        with Image.open(file_path) as img:
            img.verify()
        with Image.open(file_path) as img:
            width, height = img.size
    except (UnidentifiedImageError, OSError):
        file_path.unlink(missing_ok=True)
        return jsonify({'error': 'Uploaded file is not a valid image'}), 400

    file_size_kb = round(file_path.stat().st_size / 1024, 1)
    prediction = predict_image(str(file_path))
    knowledge = get_disease_info(prediction['plant'], prediction['disease'])

    save_prediction(
        image_path=final_name,
        plant=prediction['plant'],
        disease=prediction['disease'],
        plant_confidence=prediction['plant_confidence'],
        disease_confidence=prediction['disease_confidence'],
        is_healthy=prediction['is_healthy'],
        mode=prediction['mode'],
        width=width,
        height=height,
        file_size_kb=file_size_kb,
    )

    return jsonify({
        **prediction,
        **knowledge,
        'image_path': final_name,
        'width': width,
        'height': height,
        'file_size_kb': file_size_kb,
    })


@app.route('/api/history')
def api_history():
    return jsonify(get_history())


@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())


@app.route('/api/history/<int:prediction_id>', methods=['DELETE'])
def delete_history_item(prediction_id):
    success = delete_prediction(prediction_id)
    if success:
        return jsonify({'message': 'Deleted successfully'}), 200
    return jsonify({'error': 'Record not found'}), 404


@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    print('\nPlantGuard AI is running')
    print('Open http://127.0.0.1:5000\n')
    app.run(debug=True, host='0.0.0.0', port=5000)