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
    for region in annotation.get('highlight_regions', []):
        points = region['points']
        assert len(points) >= 3 and all(len(point) == 2 for point in points)
        assert all(vx <= x * width <= vx + vw and vy <= y * height <= vy + vh for x, y in points)
        coordinates = ' '.join(f'{x * width},{y * height}' for x, y in points)
        description = escape(label(region['label']), quote=True)
        svg.append(f'<polygon points="{coordinates}" fill="#48F447" fill-opacity=".27" aria-label="{description}"/>')
    dimension_font = height * annotation.get('dimension_font_size_height_fraction', .011)
    for dimension in annotation.get('dimension_labels', []):
        # The render's own dimension text (Solid Edge PMI) is covered and redrawn at a readable size.
        x0, y0, x1, y1 = dimension['cover']
        assert 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1
        svg.append(f'<rect x="{x0 * width}" y="{y0 * height}" width="{(x1 - x0) * width}" height="{(y1 - y0) * height}" fill="white"/>')
        ax, ay = dimension['at'][0] * width, dimension['at'][1] * height
        assert vx <= ax <= vx + vw and vy <= ay <= vy + vh, 'Framing clips a dimension label'
        lines = dimension['text']
        rotate = dimension.get('rotate', 0)
        assert rotate in (0, -90)
        half_w = max(len(line) for line in lines) * dimension_font * .29 + dimension_font * .3
        half_h = len(lines) * dimension_font * .6 + dimension_font * .15
        svg.append(f'<g transform="translate({ax} {ay}) rotate({rotate})" font-family="Arial, sans-serif" font-size="{dimension_font}" fill="#5D4B7D" text-anchor="middle">'
                   f'<rect x="{-half_w}" y="{-half_h}" width="{2 * half_w}" height="{2 * half_h}" fill="white"/>')
        for i, line in enumerate(lines):
            svg.append(f'<text y="{(i - (len(lines) - 1) / 2) * dimension_font * 1.15}" dy=".35em">{escape(line)}</text>')
        svg.append('</g>')
    note_font = height * annotation.get('note_font_size_height_fraction', .012)
    for note in annotation.get('notes', []):
        # Translatable notes: blue text with an optional leader to the dimension it names.
        nx, ny = note['at'][0] * width, note['at'][1] * height
        anchor = note.get('anchor', 'start')
        assert anchor in ('start', 'middle', 'end')
        words, lines = label(note['label']).split(), ['']
        for word in words:
            lines[-1:] = [lines[-1] + ' ' + word] if len(lines[-1]) + len(word) < note.get('wrap_chars', 22) or not lines[-1] else [lines[-1], word]
        lines = [line.strip() for line in lines]
        rotate = note.get('rotate', 0)
        assert rotate in (0, -90)
        group = []
        if 'leader' in note:
            tx, ty = note['leader'][0] * width, note['leader'][1] * height
            sx = nx + {'start': -.3, 'middle': 0, 'end': .3}[anchor] * note_font
            group.append(f'<line x1="{sx}" y1="{ny}" x2="{tx}" y2="{ty}" stroke="#1F5FA8" stroke-width="1" vector-effect="non-scaling-stroke"/>')
        group.append(f'<g transform="translate({nx} {ny}) rotate({rotate})" font-family="Arial, sans-serif" font-size="{note_font}" fill="#1F5FA8" text-anchor="{anchor}">')
        # A white backing keeps a note readable where it sits on a dimension line.
        text_w = max(len(line) for line in lines) * note_font * .52 + note_font * .4
        left = {'start': -note_font * .2, 'middle': -text_w / 2, 'end': -text_w + note_font * .2}[anchor]
        half_h = len(lines) * note_font * .6 + note_font * .1
        group.append(f'<rect x="{left}" y="{-half_h}" width="{text_w}" height="{2 * half_h}" fill="white"/>')
        for i, line in enumerate(lines):
            group.append(f'<text y="{(i - (len(lines) - 1) / 2) * note_font * 1.2}" dy=".35em">{escape(line)}</text>')
        svg.extend(group + ['</g>'])
    numbers = []
    for callout in annotation.get('callouts', []):
        number = callout['number']
        assert isinstance(number, int) and number > 0 and number not in numbers
        numbers.append(number)
        targets = callout['targets'] if 'targets' in callout else [callout['target']]
        assert targets
        assert all(0 <= value <= 1 for point in targets for value in point)
        assert 0 <= callout['badge'][0] <= 1 + padding and 0 <= callout['badge'][1] <= 1
        bx, by = callout['badge'][0] * width, callout['badge'][1] * height
        badge_text = callout.get('badge_text')
        half_width = max(radius, font_size * (len(badge_text) * .34 + .35)) if badge_text else radius
        assert radius <= bx <= canvas_width - radius and radius <= by <= height - radius
        assert vx + half_width <= bx <= vx + vw - half_width and vy + radius <= by <= vy + vh - radius, 'Framing clips a callout'
        callout_label = escape(label(callout['label']), quote=True)
        svg.append(f'<g data-callout-number="{number}" aria-label="{number}: {callout_label}">')
        for x, y in targets:
            assert vx <= x * width <= vx + vw and vy <= y * height <= vy + vh, 'Framing clips a callout target'
            svg.append(f'<line x1="{x * width}" y1="{y * height}" x2="{bx}" y2="{by}" stroke="#D6383C" stroke-width="1.2" vector-effect="non-scaling-stroke"/>')
        if badge_text:
            svg.append(f'<rect x="{bx - half_width}" y="{by - radius}" width="{2 * half_width}" height="{2 * radius}" rx="{radius / 2}" fill="#D6383C"/>')
        else:
            svg.append(f'<circle cx="{bx}" cy="{by}" r="{radius}" fill="#D6383C"/>')
        display = escape(badge_text) if badge_text else str(number)
        svg.append(f'<text x="{bx}" y="{by}" dy=".35em" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-weight="bold" font-size="{font_size}">{display}</text></g>')
    svg.append('</svg>')
    return {**image, 'svg': ''.join(svg), 'callouts': annotation.get('callouts', [])}
