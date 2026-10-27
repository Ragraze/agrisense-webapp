from io import BytesIO
from pathlib import Path
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as api


def image_file():
    buffer = BytesIO()
    Image.new('RGB', (50, 50), (255, 255, 255)).save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


def test_health_and_swagger():
    client = api.app.test_client()
    assert client.get('/api/health').json['status'] == 'ok'
    spec = client.get('/apispec_1.json')
    assert spec.status_code == 200
    assert '/api/predict' in spec.json['paths']
    assert client.get('/apidocs/').status_code == 200


def test_reject_invalid_uploads():
    client = api.app.test_client()
    assert client.post('/api/predict').status_code == 400
    assert client.post('/api/predict', data={'image': (BytesIO(b'bad'), 'bad.png')}).status_code == 400
    assert client.post('/api/predict', data={'image': (BytesIO(b'a' * (8 * 1024 * 1024)), 'large.png')}).status_code == 413


def test_preprocessing_and_prediction(monkeypatch):
    class Runner:
        def get_input_details(self):
            return [{'shape': [1, 160, 160, 3], 'dtype': np.float32, 'index': 0}]
        def get_output_details(self):
            return [{'index': 1}]
        def set_tensor(self, index, value):
            assert value.shape == (1, 160, 160, 3)
            assert value.dtype == np.float32
            assert np.allclose(value, 1)
        def invoke(self):
            pass
        def get_tensor(self, index):
            return np.array([[2.0]], dtype=np.float32)
    monkeypatch.setattr(api, 'get_interpreter', lambda: Runner())
    response = api.app.test_client().post('/api/predict', data={'image': (image_file(), 'rice.png')})
    assert response.status_code == 200
    assert response.json['label'] == 'Ripe'
    assert abs(response.json['confidence'] - 0.880797) < 0.00001


def test_model_failure(monkeypatch):
    def unavailable():
        raise RuntimeError('Unavailable')
    monkeypatch.setattr(api, 'get_interpreter', unavailable)
    response = api.app.test_client().post('/api/predict', data={'image': (image_file(), 'rice.png')})
    assert response.status_code == 503
    assert 'error' in response.json


def test_evaluation_report_and_model_fingerprint(monkeypatch, tmp_path):
    import hashlib
    import json
    model = tmp_path / 'model.tflite'
    model.write_bytes(b'model-v1')
    report = tmp_path / 'evaluation.json'
    monkeypatch.setattr(api, 'MODEL_PATH', model)
    monkeypatch.setattr(api, 'EVALUATION_PATH', report)
    client = api.app.test_client()
    assert client.get('/api/evaluation').status_code == 404
    report.write_text(json.dumps({'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest(), 'accuracy': 0.9}))
    response = client.get('/api/evaluation')
    assert response.status_code == 200
    assert response.json['accuracy'] == 0.9
    model.write_bytes(b'model-v2')
    assert client.get('/api/evaluation').status_code == 409
    report.write_text('{invalid')
    assert client.get('/api/evaluation').status_code == 503


def test_classification_metrics():
    from evaluate import classification_metrics
    metrics = classification_metrics([[8, 2], [1, 9]])
    assert metrics['sample_count'] == 20
    assert metrics['correct_count'] == 17
    assert metrics['accuracy'] == 0.85
    assert abs(metrics['per_class']['Raw']['precision'] - 8 / 9) < 1e-10
    assert metrics['per_class']['Raw']['recall'] == 0.8
    assert abs(metrics['per_class']['Ripe']['f1'] - 18 / 21) < 1e-10
    zero_predictions = classification_metrics([[2, 0], [2, 0]])
    assert zero_predictions['per_class']['Ripe']['precision'] == 0
    assert zero_predictions['per_class']['Ripe']['f1'] == 0


def test_dataset_inventory_and_report_errors(monkeypatch, tmp_path):
    from dataset_report import inventory
    import json
    for split in ['train', 'valid', 'test']:
        for label in ['Raw', 'Ripe']:
            folder = tmp_path / 'dataset' / split / label
            folder.mkdir(parents=True)
            (folder / 'sample.jpg').write_bytes(b'counted-as-an-image-file')
            (folder / 'notes.txt').write_text('not an image')
    report = inventory(tmp_path / 'dataset')
    assert report['total'] == 6
    assert report['class_totals'] == {'Raw': 3, 'Ripe': 3}
    assert [s['total'] for s in report['splits']] == [2, 2, 2]
    path = tmp_path / 'dataset.json'
    monkeypatch.setattr(api, 'DATASET_REPORT_PATH', path)
    client = api.app.test_client()
    assert client.get('/api/dataset').status_code == 404
    path.write_text(json.dumps(report))
    assert client.get('/api/dataset').json['total'] == 6
    path.write_text('invalid')
    assert client.get('/api/dataset').status_code == 503
