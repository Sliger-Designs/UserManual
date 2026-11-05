#!/usr/bin/env python3
"""Archive each product page's primary cover photo and prepare a build copy."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen

from bs4 import BeautifulSoup
from PIL import Image, ImageOps

from manual_paths import web_slug

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', nargs='+', default=['CX3150a', 'CX3150i', 'CX3150x', 'CX3151a', 'CX3151i', 'CX3151x', 'CX3152a', 'CX3152i', 'CX3170a', 'CX3171a', 'CX3172a', 'CX3170aXL', 'CX3170iXL', 'CX3171aXL', 'CX3171iXL', 'CX3172aXL', 'CX3172iXL', 'CX4150a', 'CX4150e', 'CX4150i', 'CX4170a', 'CX4170e', 'CX4170i', 'CX4200a', 'CX4200e', 'CX4200f', 'CX4200i', 'CX4712', 'CX4713', 'S630', 'S640'])
    args = parser.parse_args()
    archive = ROOT / 'sources/web/covers'
    output = ROOT / 'illustrations/published/covers'
    archive.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    for model in args.models:
        page_url = 'https://sliger.com/products/' + web_slug(model)
        with urlopen(page_url, timeout=30) as response:
            soup = BeautifulSoup(response.read(), 'html.parser')
        product = json.loads(soup.find('product-page')[':product'])
        assert product['part_number'].lower() == model.lower(), model
        url = product['cover_photos'][0]
        with urlopen(url, timeout=30) as response:
            data = response.read()
        checksum = hashlib.sha256(data).hexdigest()
        source = archive / f'{model}-{checksum[:12]}.webp'
        source.write_bytes(data)
        with Image.open(io.BytesIO(data)) as original:
            image = ImageOps.exif_transpose(original).convert('RGB')
            image.thumbnail((2400, 1800), Image.Resampling.LANCZOS)
            target = output / f'{model}-{checksum[:12]}.jpg'
            image.save(target, quality=94, subsampling=0, optimize=True)
            dimensions = list(image.size)
        manifest[model] = {
            'path': target.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'source_path': source.relative_to(ROOT).as_posix(), 'source_sha256': checksum,
            'product_url': page_url, 'image_url': url,
            'retrieved_at': datetime.now(timezone.utc).isoformat(),
            'selection': 'First entry in product cover_photos; primary website image.',
            'transformation': 'EXIF orientation; fit within 2400x1800 without upscaling; no crop; RGB JPEG quality 94.',
            'dimensions_px': dimensions,
        }
        print(model, url, dimensions)
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
