"""Evaluate the supplied model on labeled test images without retraining it."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from tflite_runtime.interpreter import Interpreter

from inference import infer_image

ROOT = Path(__file__).resolve().parents[1]
LABELS = ['Raw', 'Ripe']
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def classification_metrics(matrix):
    total = sum(sum(row) for row in matrix)
    if not total:
        raise ValueError('No samples to evaluate')
    classes = {}
    for index, label in enumerate(LABELS):
        tp = matrix[index][index]
        support = sum(matrix[index])
        predicted = sum(row[index] for row in matrix)
        precision = tp / predicted if predicted else 0.0
        recall = tp / support if support else 0.0
        classes[label] = {'precision': precision, 'recall': recall,
                          'f1': 2 * tp / (support + predicted) if support + predicted else 0.0,
                          'support': support}
    return {
        'accuracy': sum(matrix[i][i] for i in range(2)) / total,
        'macro_avg': {metric: sum(c[metric] for c in classes.values()) / 2 for metric in ['precision', 'recall', 'f1']},
        'per_class': classes,
        'sample_count': total,
        'correct_count': sum(matrix[i][i] for i in range(2)),
        'confusion_matrix': matrix,
    }


def files_in(directory):
    return sorted(p for p in directory.rglob('*') if p.is_file() and p.suffix.lower() in EXTENSIONS)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(model_path, dataset_path):
    runner = Interpreter(model_path=str(model_path), num_threads=2)
    runner.allocate_tensors()
    matrix = [[0, 0], [0, 0]]
    predictions = []
    manifest = hashlib.sha256()
    seen = set()
    duplicate_count = 0
    other_hashes = {digest(p) for split in ['train', 'valid'] for p in files_in(dataset_path / split)}
    overlap_count = 0
    for actual, label in enumerate(LABELS):
        files = files_in(dataset_path / 'test' / label)
        if not files:
            raise ValueError(f'Missing test images for {label}')
        for path in files:
            image_hash = digest(path)
            duplicate_count += image_hash in seen
            overlap_count += image_hash in other_hashes
            seen.add(image_hash)
            relative = path.relative_to(dataset_path).as_posix()
            manifest.update(f'{relative}:{image_hash}\n'.encode())
            with Image.open(path) as image:
                logit, probability = infer_image(image, runner)
            predicted = int(logit > 0)
            matrix[actual][predicted] += 1
            predictions.append({'file': relative, 'actual': label, 'predicted': LABELS[predicted], 'ripe_probability': probability})
        print(f'{label}: {len(files)} images evaluated', flush=True)
    return {
        'schema_version': 1,
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'model': 'MobileNetV2', 'model_sha256': digest(model_path),
        'dataset': 'dataset/test', 'dataset_sha256': manifest.hexdigest(),
        'labels': LABELS, 'threshold': 'logit > 0 = Ripe; otherwise Raw',
        'preprocessing': 'EXIF orientation, RGB, bilinear resize to model input, pixel / 127.5 - 1',
        'input_shape': runner.get_input_details()[0]['shape'].tolist(),
        'exact_duplicate_test_images': duplicate_count,
        'exact_test_overlap_with_train_valid': overlap_count,
        'skipped_count': 0,
        **classification_metrics(matrix),
        'limitations': [
            'Labels follow the dataset folder names and the notebook mapping; labels have not been independently audited.',
            'Exact-byte overlap checks do not detect resized, augmented, or adjacent video frames. The data split is not verified to be independent.',
            'These metrics describe the included test split, not field accuracy or harvest timing.',
        ],
        'predictions': predictions,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, default=ROOT / 'tflite/rice_plant_model.tflite')
    parser.add_argument('--dataset', type=Path, default=ROOT / 'dataset')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'reports/evaluation.json')
    args = parser.parse_args()
    report = evaluate(args.model, args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp = args.output.with_suffix('.tmp')
    temp.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    temp.replace(args.output)
    print(json.dumps({key: report[key] for key in ['sample_count', 'accuracy', 'macro_avg', 'confusion_matrix', 'exact_test_overlap_with_train_valid']}, indent=2))
