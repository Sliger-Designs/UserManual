#!/usr/bin/env python3
"""Prepare only referenced publication images. Originals remain untouched."""
import hashlib
import argparse
import json
from pathlib import Path
from manual_assets import pending_image
from manual_paths import MODEL_CATEGORIES, REFERENCE_INVENTORY, content_directory, inventory_path, published_directory
from PIL import Image, ImageOps
from background_cleanup import white_background
from color_adjustment import shift_hue_band

COLOUR_SETTINGS = ('hue_range_deg', 'hue_shift_deg', 'saturation_scale', 'value_scale', 'min_saturation')

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='CX3150a', choices=sorted(MODEL_CATEGORIES))
    parser.add_argument('--only', nargs='+', help='Prepare only these selected asset keys; retain other existing publication copies.')
    args = parser.parse_args()
    model = args.model
    manual = json.loads((content_directory(model) / 'manual.json').read_text())
    inventory = json.loads(inventory_path(model).read_text())
    entries = {x['original_filename']: x for x in inventory['items']}
    common = json.loads(inventory_path('common').read_text())
    entries.update({x['asset_key']: x for x in common['items']})
    reference = json.loads(REFERENCE_INVENTORY.read_text())
    entries.update({x['asset_key']: x for x in reference['items']})
    names = sorted({name for page in manual['pages'] for group in [page, *page.get('steps', [])] for name in group.get('images', [])
                    if pending_image(name) is None})
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
    common_manifest = published_directory('common') / 'manifest.json'
    model_manifest = published_directory(model) / 'manifest.json'
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
        # Shared copies serve every manual: keep an existing one made from this same original,
        # since re-encoding is not byte-identical and would change other manuals' assets.
        cleanup = entry.get('background_cleanup')
        # Cleaned copies are lossless PNG unless the entry asks for JPEG (rackmount, to keep the repository small).
        cleaned_png = bool(cleanup) and cleanup.get('publication_format', 'png') == 'png'
        suffix = '.png' if original.suffix.lower() == '.png' or cleaned_png else '.jpg'
        colour = entry.get('color_adjustment')
        colour_settings = {key: colour[key] for key in COLOUR_SETTINGS if key in colour} if colour else None
        previous = manifests[group].get(name)
        if (group == 'common' and previous and previous['source_sha256'] == entry['sha256']
                and previous['path'].endswith(suffix)
                and bool(previous.get('background_cleanup')) == bool(cleanup)
                and {key: value for key, value in previous.get('color_adjustment', {}).items() if key in COLOUR_SETTINGS} == (colour_settings or {})
                and (ROOT / previous['path']).exists()
                and hashlib.sha256((ROOT / previous['path']).read_bytes()).hexdigest() == previous['sha256']):
            continue
        output = published_directory(group)
        output.mkdir(parents=True, exist_ok=True)
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
            colour_report = None
            if colour:  # after resizing: the same result at a fraction of the memory for 9000 px renders
                assert image.mode == 'RGB', (name, 'colour adjustment supports RGB publication copies')
                image, colour_report = shift_hue_band(image, **colour_settings)
            if suffix == '.png':
                image.save(target, optimize=True)
            else:
                image.save(target, quality=90, optimize=True, subsampling=0)
            dimensions = list(image.size)
        transformation = 'EXIF orientation; fit within 1800x1400 without upscaling; no crop. PNG retains transparency; JPEG uses RGB, quality 90, subsampling 0.'
        if cleanup_report:
            encoding = 'lossless RGB PNG' if suffix == '.png' else 'RGB JPEG quality 90, subsampling 0'
            transformation = f'EXIF orientation; flat gray background replaced with white before resizing; fit within 1800x1400 without upscaling; no crop; {encoding}. Full-resolution cleaned copy saved separately; original unchanged.'
        if colour_report:
            transformation += ' Part colour matched to the manual orange after resizing (color_adjustment); original unchanged.'
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
        if colour_report:
            manifests[group][name]['color_adjustment'] = colour_report
    for group, manifest in manifests.items():
        (published_directory(group) / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Prepared {len(names)} selected publication assets; originals unchanged.')

if __name__ == '__main__':
    main()
