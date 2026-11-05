#!/usr/bin/env python3
"""Record every staged full-resolution original for a model in illustrations/<model>.inventory.json.

Originals live in the ignored illustrations/<category>/<model>/ folder (see illustrations/README.md).
Existing entries keep their selection status and notes; new files are added as candidates, and
files no longer present are reported rather than silently dropped."""
import argparse
import hashlib
import json

from PIL import Image

from manual_paths import MODEL_CATEGORIES, ROOT

IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp', '.bmp'}
Image.MAX_IMAGE_PIXELS = None  # Trusted CAD renders exceed Pillow's decompression-bomb default.


def entry_id(model, filename):
    return f'{model.lower()}-{hashlib.sha256(filename.encode()).hexdigest()[:12]}'


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--model', required=True, choices=sorted(MODEL_CATEGORIES))
    parser.add_argument('--note', default='Supplied original; configuration applicability requires reference review.')
    args = parser.parse_args()
    folder = ROOT / 'illustrations' / MODEL_CATEGORIES[args.model] / args.model
    if not folder.is_dir():
        raise SystemExit(f'Stage the originals in {folder.relative_to(ROOT)} first')
    path = ROOT / f'illustrations/{args.model}.inventory.json'
    existing = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'schema_version': 1, 'model': args.model, 'items': []}
    previous = {item['original_filename']: item for item in existing['items']}
    items, added, changed = [], 0, []
    for file in sorted(folder.iterdir(), key=lambda f: f.name):
        if file.suffix.lower() not in IMAGE_SUFFIXES or not file.is_file():
            continue
        data = file.read_bytes()
        with Image.open(file) as image:
            width, height, image_format = image.width, image.height, image.format
        record = {
            'id': entry_id(args.model, file.name), 'original_filename': file.name,
            'local_path': file.relative_to(ROOT).as_posix(), 'width_px': width, 'height_px': height,
            'format': image_format, 'size_bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'selection_status': 'candidate', 'note': args.note,
        }
        old = previous.pop(file.name, None)
        if old:
            if old['sha256'] != record['sha256']:
                changed.append(file.name)
            record = {**record, **{k: v for k, v in old.items() if k not in {'width_px', 'height_px', 'format', 'size_bytes', 'sha256', 'local_path'}}}
        else:
            added += 1
        items.append(record)
    existing['items'] = items
    path.write_text(json.dumps(existing, indent=2) + '\n', encoding='utf-8')
    print(f'{path.relative_to(ROOT)}: {len(items)} originals, {added} added')
    for name in changed:
        print(f'  CHANGED original (re-check callouts and publication copies): {name}')
    for name in previous:
        print(f'  MISSING original, removed from inventory: {name}')


if __name__ == '__main__':
    main()
