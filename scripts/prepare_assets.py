#!/usr/bin/env python3
"""Prepare only referenced publication images. Originals remain untouched."""
import hashlib
import argparse
import json
from pathlib import Path
from manual_paths import content_directory
from PIL import Image, ImageOps
from background_cleanup import white_background

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='CX3150a', choices=['CX3150a', 'CX4170a', 'S630', 'S640'])
    parser.add_argument('--only', nargs='+', help='Prepare only these selected asset keys; retain other existing publication copies.')
    args = parser.parse_args()
    model = args.model
    manual = json.loads((content_directory(model) / 'manual.json').read_text())
    inventory = json.loads((ROOT / f'illustrations/{model}.inventory.json').read_text())
    entries = {x['original_filename']: x for x in inventory['items']}
    common = json.loads((ROOT / 'illustrations/common.inventory.json').read_text())
    entries.update({x['asset_key']: x for x in common['items']})
    reference = json.loads((ROOT / 'illustrations/reference.inventory.json').read_text())
    entries.update({x['asset_key']: x for x in reference['items']})
    names = sorted({name for page in manual['pages'] for group in [page, *page.get('steps', [])] for name in group.get('images', [])})
    # Vector compositions can reference a detail from a second unchanged render.
    for page in manual['pages']:
        for group in [page, *page.get('steps', [])]:
            for annotation_path in group.get('image_annotations', {}).values():
                annotation = json.loads((content_directory(model) / annotation_path).read_text())
                names = sorted(set(names) | {fragment['asset_key'] for fragment in annotation.get('image_fragments', [])})
    if manual.get('family') == 'sff':
        hardware = json.loads((content_directory(model) / 'hardware.json').read_text())
        names = sorted(set(names) | {name for item in hardware['items']
                       for name in [item.get('image'), *item.get('detail_images', [])] if name})
    common_manifest = ROOT / 'illustrations/published/common/manifest.json'
    model_manifest = ROOT / f'illustrations/published/{model}/manifest.json'
    manifests = {model: json.loads(model_manifest.read_text()) if args.only and model_manifest.exists() else {},
                 'common': json.loads(common_manifest.read_text()) if common_manifest.exists() else {}}
    if args.only:
        assert set(args.only) <= set(names), 'Requested assets must be referenced by this manual'
        names = sorted(set(args.only))
    for name in names:
        entry = entries[name]
        assert entry['selection_status'] != 'excluded_unsupported_configuration', name
        original = ROOT / entry['local_path']
        assert hashlib.sha256(original.read_bytes()).hexdigest() == entry['sha256'], name
        group = 'common' if name.startswith('common/') else model
        output = ROOT / 'illustrations/published' / group
        output.mkdir(parents=True, exist_ok=True)
        cleanup = entry.get('background_cleanup')
        suffix = '.png' if original.suffix.lower() == '.png' or cleanup else '.jpg'
        target = output / (entry['id'] + suffix)
        with Image.open(original) as image:
            image = ImageOps.exif_transpose(image)
            cleanup_report = None
            if cleanup:
                image, cleanup_report = white_background(image, cleanup['reference_rgb'], cleanup['tolerance_per_channel'])
                full_resolution = ROOT / cleanup['full_resolution_path']
                full_resolution.parent.mkdir(parents=True, exist_ok=True)
                image.save(full_resolution, optimize=True)
                cleanup_report.update({
                    'full_resolution_path': cleanup['full_resolution_path'],
                    'full_resolution_dimensions_px': list(image.size),
                    'full_resolution_sha256': hashlib.sha256(full_resolution.read_bytes()).hexdigest(),
                })
            else:
                image = image.convert('RGBA' if suffix == '.png' else 'RGB')
            image.thumbnail((1800, 1400), Image.Resampling.LANCZOS)
            if suffix == '.png':
                image.save(target, optimize=True)
            else:
                image.save(target, quality=90, optimize=True, subsampling=0)
            dimensions = list(image.size)
        transformation = 'EXIF orientation; fit within 1800x1400 without upscaling; no crop. PNG retains transparency; JPEG uses RGB, quality 90, subsampling 0.'
        if cleanup_report:
            transformation = 'EXIF orientation; flat gray background replaced with white before resizing; fit within 1800x1400 without upscaling; no crop; lossless RGB PNG. Full-resolution cleaned copy saved separately; original unchanged.'
        manifests[group][name] = {
            'path': target.relative_to(ROOT).as_posix(),
            'source_path': entry['local_path'], 'source_sha256': entry['sha256'],
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'dimensions_px': dimensions,
            'transformation': transformation,
            'status': 'prototype_selection_needs_review',
        }
        if cleanup_report:
            manifests[group][name]['background_cleanup'] = cleanup_report
    for group, manifest in manifests.items():
        (ROOT / 'illustrations/published' / group / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Prepared {len(names)} selected publication assets; originals unchanged.')

if __name__ == '__main__':
    main()
