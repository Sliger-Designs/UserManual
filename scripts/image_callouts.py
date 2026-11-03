"""Render vector callouts in the same coordinate system as an unchanged image."""
from html import escape
import json
from pathlib import Path


def with_callouts(image, annotation_path, asset, image_fragments=None, label=lambda text: text):
    """`label` localizes callout accessibility labels (identity for English)."""
    annotation = json.loads(Path(annotation_path).read_text(encoding='utf-8'))
    assert annotation['asset_key'] == image['key']
    assert annotation['source_sha256'] == asset['source_sha256'], 'Image changed; review callout positions: ' + image['key']
    assert annotation['coordinate_space'] == 'uncropped_image'
    assert 'no crop' in asset['transformation'], 'Cropped images require new callout positions'
    width, height = asset['dimensions_px']
    assert abs(width / height - annotation['aspect_ratio']) < .005, 'Image aspect ratio changed; review callouts'
    padding = annotation.get('right_padding_fraction', 0)
    assert 0 <= padding <= 1
    canvas_width = width * (1 + padding)
    radius = height * annotation['badge_radius_height_fraction'] if 'badge_radius_height_fraction' in annotation else width * .022
    font_size = height * annotation['font_size_height_fraction'] if 'font_size_height_fraction' in annotation else width * .025
    assert radius > 0 and font_size > 0
    # Frame the unchanged source image without moving its annotation coordinates.
    view_box = annotation.get('view_box', [0, 0, 1 + padding, 1])
    assert len(view_box) == 4
    vx, vy, vw, vh = [value * scale for value, scale in zip(view_box, (width, height, width, height))]
    assert vx >= 0 and vy >= 0 and vw > 0 and vh > 0
    assert vx + vw <= canvas_width + .001 and vy + vh <= height + .001
    title = escape(image['alt'], quote=True)
    svg = [f'<svg class="annotated-image" xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" role="img" aria-label="{title}" preserveAspectRatio="xMidYMid meet">',
           f'<image href="{image["src"]}" width="{width}" height="{height}"/>']
    for fragment in image_fragments or []:
        source_rect = fragment['source_rect']
        destination = fragment['destination_rect']
        for rect in (source_rect, destination):
            assert len(rect) == 4 and all(0 <= value <= 1 for value in rect)
            assert rect[2] > 0 and rect[3] > 0
            assert rect[0] + rect[2] <= 1 and rect[1] + rect[3] <= 1
        fw, fh = fragment['dimensions_px']
        sx, sy, sw, sh = [value * scale for value, scale in zip(source_rect, (fw, fh, fw, fh))]
        dx, dy, dw, dh = [value * scale for value, scale in zip(destination, (width, height, width, height))]
        assert abs((sw / sh) / (dw / dh) - 1) < .005, 'Fragment must preserve source proportions'
        assert vx <= dx and vy <= dy and dx + dw <= vx + vw and dy + dh <= vy + vh, 'Framing clips an image fragment'
        fragment_label = escape(fragment['label'], quote=True)
        svg.append(f'<svg x="{dx}" y="{dy}" width="{dw}" height="{dh}" '
                   f'viewBox="{sx} {sy} {sw} {sh}" overflow="hidden" '
                   f'aria-label="{fragment_label}" data-image-fragment="{escape(fragment["asset_key"], quote=True)}">'
                   f'<image href="{fragment["src"]}" width="{fw}" height="{fh}"/></svg>')
    numbers = []
    for callout in annotation['callouts']:
        number = callout['number']
        assert isinstance(number, int) and number > 0 and number not in numbers
        numbers.append(number)
        targets = callout['targets'] if 'targets' in callout else [callout['target']]
        assert targets
        assert all(0 <= value <= 1 for point in targets for value in point)
        assert 0 <= callout['badge'][0] <= 1 + padding and 0 <= callout['badge'][1] <= 1
        bx, by = callout['badge'][0] * width, callout['badge'][1] * height
        assert radius <= bx <= canvas_width - radius and radius <= by <= height - radius
        assert vx + radius <= bx <= vx + vw - radius and vy + radius <= by <= vy + vh - radius, 'Framing clips a callout'
        callout_label = escape(label(callout['label']), quote=True)
        svg.append(f'<g data-callout-number="{number}" aria-label="{number}: {callout_label}">')
        for x, y in targets:
            assert vx <= x * width <= vx + vw and vy <= y * height <= vy + vh, 'Framing clips a callout target'
            svg.append(f'<line x1="{x * width}" y1="{y * height}" x2="{bx}" y2="{by}" stroke="#D6383C" stroke-width="1.2" vector-effect="non-scaling-stroke"/>')
        svg.extend([
            f'<circle cx="{bx}" cy="{by}" r="{radius}" fill="#D6383C"/>',
            f'<text x="{bx}" y="{by}" dy=".35em" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-weight="bold" font-size="{font_size}">{number}</text></g>'])
    svg.append('</svg>')
    return {**image, 'svg': ''.join(svg), 'callouts': annotation['callouts']}
