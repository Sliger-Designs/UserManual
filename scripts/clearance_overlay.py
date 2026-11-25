"""Write the notes overlay for a clearance drawing (top or front view) from a source spec, and optionally preview it.

The drawing itself is a Solid Edge render: Sliger's PMI dimensions are drawn by ERA, so the overlay only adds the
translatable notes (ALL CAPS, in the margins, angled leaders landing on the dimension lines). Positions in the spec are
pixels in `frame_px`, the render size they were measured at; renders at another width with the same camera reuse them.

    clearance_overlay.py scripts/clearance_specs/CX2257g-top.json [--preview out.png]

Spec keys: image (render, repo-relative), annotation (output JSON, repo-relative), frame_px [w, h], view_box_px
[x, y, w, h], note_font_size_height_fraction, review_status, notes [{label, at [x, y], anchor, leader [x, y],
wrap_chars?}]. Re-run after every re-render: the annotation records the image hash.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

from image_callouts import with_callouts

ROOT = Path(__file__).resolve().parent.parent


def build(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
    image = ROOT / spec['image']
    fw, fh = spec['frame_px']
    size = Image.open(image).size
    assert abs(size[0] / size[1] - fw / fh) < .005, 'Render aspect ratio differs from the spec frame'
    x, y, w, h = spec['view_box_px']
    annotation = {
        'asset_key': image.name,
        'source_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
        'coordinate_space': 'uncropped_image',
        'aspect_ratio': size[0] / size[1],
        'view_box': [x / fw, y / fh, w / fw, h / fh],
        'note_font_size_height_fraction': spec['note_font_size_height_fraction'],
        'review_status': spec['review_status'],
        'notes': [{'label': n['label'], 'at': [n['at'][0] / fw, n['at'][1] / fh], 'anchor': n.get('anchor', 'start'),
                   'wrap_chars': n.get('wrap_chars', 60),
                   **({'leader': [n['leader'][0] / fw, n['leader'][1] / fh]} if 'leader' in n else {})}
                  for n in spec['notes']],
        'callouts': [],
    }
    out = ROOT / spec['annotation']
    out.write_text(json.dumps(annotation, indent=2) + '\n', encoding='utf-8', newline='\n')
    return image, out, size


def preview(image, annotation, size, png):
    result = with_callouts({'key': image.name, 'src': image.resolve().as_uri(), 'alt': image.stem}, annotation,
                           {'source_sha256': json.loads(annotation.read_text(encoding='utf-8'))['source_sha256'],
                            'transformation': 'no crop', 'dimensions_px': list(size)})
    html = Path(png).with_suffix('.html')
    html.write_text(f"<html><body style='margin:0;background:white'><div style='width:2400px'>{result['svg']}</div></body></html>",
                    encoding='utf-8')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 2400, 'height': 800})
        page.goto(html.resolve().as_uri())
        page.wait_for_timeout(1500)
        page.screenshot(path=str(png), full_page=True)
        browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('spec')
    parser.add_argument('--preview')
    args = parser.parse_args()
    image, out, size = build(args.spec)
    print('wrote', out.relative_to(ROOT))
    if args.preview:
        preview(image, out, size, args.preview)
        print('preview', args.preview)
