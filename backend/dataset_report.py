"""Create a small dataset inventory that can be shipped without image files."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = ['Raw', 'Ripe']
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def inventory(dataset):
    splits = []
    for name in ['train', 'valid', 'test']:
        counts = {}
        for label in LABELS:
            folder = dataset / name / label
            if not folder.is_dir():
                raise ValueError(f'Missing dataset directory: {folder}')
            counts[label] = sum(p.is_file() and p.suffix.lower() in EXTENSIONS for p in folder.rglob('*'))
        splits.append({'name': name, 'counts': counts, 'total': sum(counts.values())})
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'name': 'Paddy', 'version': '1', 'labels': LABELS,
        'source_url': 'https://universe.roboflow.com/agrisense-dataset/paddy-o34tk',
        'license': 'CC BY 4.0',
        'metadata_source': 'dataset/README.dataset.txt; dataset/README.roboflow.txt',
        'exported_at': '2024-06-11',
        'preprocessing': ['EXIF auto-orientation', 'Resize to 640 × 640 (stretch)'],
        'augmentation': 'No augmentation applied during the documented Roboflow export.',
        'splits': splits,
        'total': sum(split['total'] for split in splits),
        'class_totals': {label: sum(split['counts'][label] for split in splits) for label in LABELS},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=ROOT / 'dataset')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'reports/dataset.json')
    args = parser.parse_args()
    result = inventory(args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(result, indent=2) + '\n')
    temporary.replace(args.output)
    print(json.dumps(result, indent=2))
