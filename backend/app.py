import hashlib
import json
import os
from io import BytesIO
from pathlib import Path
from threading import Lock

from PIL import Image, ImageOps, UnidentifiedImageError
from flask import Flask, jsonify, request
from flasgger import Swagger
from werkzeug.exceptions import RequestEntityTooLarge
from inference import infer_image

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT / "tflite/rice_plant_model.tflite"))
app = Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=8 * 1024 * 1024, SWAGGER={"title": "AgriSense API", "uiversion": 3})
Swagger(app, template={"info": {"title": "AgriSense API", "version": "1.0.0", "description": "Klasifikasi kematangan padi dengan MobileNetV2."}})
lock = Lock()
interpreter = None
EVALUATION_PATH = Path(os.getenv("EVALUATION_PATH", Path(__file__).parent / "reports/evaluation.json"))
DATASET_REPORT_PATH = Path(__file__).parent / "reports/dataset.json"


def get_interpreter():
    global interpreter
    if interpreter is None:
        from tflite_runtime.interpreter import Interpreter
        interpreter = Interpreter(model_path=str(MODEL_PATH), num_threads=2)
        interpreter.allocate_tensors()
    return interpreter


@app.errorhandler(RequestEntityTooLarge)
def too_large(_):
    return jsonify(error="Ukuran gambar maksimal 8 MB."), 413


@app.get("/api/health")
def health():
    """Status layanan dan berkas model.
    ---
    responses:
      200:
        description: Layanan aktif; model_available menunjukkan keberadaan berkas, bukan kesiapan inferensi.
    """
    return jsonify(status="ok", model_available=MODEL_PATH.is_file())


@app.get("/api/model")
def model_info():
    """Informasi metode penelitian.
    ---
    responses:
      200:
        description: Arsitektur, kelas, dan praproses model.
    """
    return jsonify(architecture="MobileNetV2", method="Transfer learning", classes=["Raw", "Ripe"], normalization="pixel / 127.5 - 1", source="notebook/fix_notebook.ipynb", model_available=MODEL_PATH.is_file())


@app.get("/api/dataset")
def dataset_info():
    """Inventaris dataset dan atribusi sumber.
    ---
    responses:
      200:
        description: Jumlah gambar per split/kelas dan metadata sumber.
      404:
        description: Inventaris belum dibuat.
      503:
        description: Inventaris tidak dapat dibaca.
    """
    if not DATASET_REPORT_PATH.is_file():
        return jsonify(error="Informasi dataset belum tersedia. Buat inventaris dataset di server."), 404
    try:
        return jsonify(json.loads(DATASET_REPORT_PATH.read_text()))
    except (OSError, ValueError):
        app.logger.exception("Dataset report unavailable")
        return jsonify(error="Informasi dataset tidak dapat dibaca. Periksa laporan di server."), 503


@app.get("/api/evaluation")
def evaluation():
    """Hasil evaluasi offline pada seluruh dataset/test.
    ---
    responses:
      200:
        description: Metrik, confusion matrix, dan metadata evaluasi model.
      404:
        description: Laporan belum dibuat.
      409:
        description: Model aktif berbeda dari model yang dievaluasi.
      503:
        description: Laporan atau model tidak dapat dibaca.
    """
    if not EVALUATION_PATH.is_file():
        return jsonify(error="Evaluasi belum tersedia. Jalankan skrip evaluasi pada server."), 404
    try:
        report = json.loads(EVALUATION_PATH.read_text())
        current_hash = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()
        if report['model_sha256'] != current_hash:
            return jsonify(error="Model telah berubah. Jalankan ulang evaluasi agar metrik sesuai model aktif."), 409
        return jsonify(report)
    except (OSError, ValueError, KeyError):
        app.logger.exception("Evaluation report unavailable")
        return jsonify(error="Laporan evaluasi tidak dapat dibaca. Periksa laporan dan model pada server."), 503


@app.post("/api/predict")
def predict():
    """Prediksi kematangan padi dari gambar.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Gambar JPEG, PNG, atau WebP, maksimal 8 MB.
    responses:
      200:
        description: Kelas, probabilitas, dan skor logit model.
      400:
        description: Gambar tidak valid.
      413:
        description: Berkas melebihi 8 MB.
      503:
        description: Model belum tersedia atau gagal menjalankan inferensi.
    """
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        return jsonify(error="Pilih gambar padi terlebih dahulu."), 400
    try:
        with Image.open(BytesIO(upload.read())) as source:
            if source.format not in {"JPEG", "PNG", "WEBP"}:
                return jsonify(error="Gunakan gambar JPEG, PNG, atau WebP."), 400
            if source.width * source.height > 25_000_000:
                return jsonify(error="Resolusi gambar maksimal 25 megapiksel."), 400
            image = ImageOps.exif_transpose(source).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return jsonify(error="Berkas tidak dapat dibaca sebagai gambar."), 400
    try:
        with lock:
            score, probability = infer_image(image, get_interpreter())
        ripe = score > 0
        return jsonify(label="Ripe" if ripe else "Raw", title="Padi matang" if ripe else "Padi belum matang", confidence=probability if ripe else 1 - probability, probabilities={"Raw": 1 - probability, "Ripe": probability}, logit=score, model="MobileNetV2", note="Hasil klasifikasi gambar untuk penelitian. Konfirmasi kondisi padi di lapangan sebelum menentukan waktu panen.")
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify(error="Model belum siap. Periksa dependensi dan berkas model pada server."), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
