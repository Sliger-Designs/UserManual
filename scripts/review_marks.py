"""Review-only marks for draft builds: a coloured dot in the corner of each render borrowed from
another model, so a reviewer can see which illustrations are not the model's own. Never used
for release builds; publication files are unchanged (the dot is drawn on an in-memory copy)."""
import base64
import io
import json
import re

from PIL import Image, ImageDraw

from manual_paths import inventory_path, published_directory

# Borrowed from a model of the same family (e.g. the CX3170a for the CX3171a): blue.
# Borrowed from a different family or size (e.g. a 15-inch CX3151a for the 17-inch CX3171a): magenta.
SAME_FAMILY = (30, 136, 229)
OTHER_FAMILY = (216, 27, 96)
COPIED = re.compile(r'^Copied from illustrations/[^/]+/([^/]+)/')


def family(model):
    return model[:5]


def borrowed_sources(model):
    """{asset key: source model} for the model's published assets copied from another model."""
    manifest = json.loads((published_directory(model) / 'manifest.json').read_text(encoding='utf-8'))
    inventory = json.loads(inventory_path(model).read_text(encoding='utf-8'))['items']
    source_by_path = {}
    for item in inventory:
        match = COPIED.match(item.get('note', ''))
        if match and match.group(1) != model:
            source_by_path[item['local_path']] = match.group(1)
    return {key: source_by_path[asset['source_path']] for key, asset in manifest.items()
            if asset.get('source_path') in source_by_path}


def colour(model, source):
    return SAME_FAMILY if family(source) == family(model) else OTHER_FAMILY


def marked_data_uri(path, rgb):
    """The image with a dot just inside the top-left corner of its content (so margin cropping keeps it)."""
    image = Image.open(path)
    image.load()
    mode = image.mode
    canvas = image.convert('RGBA')
    grey = canvas.convert('L')
    box = grey.point(lambda v: 255 if v < 240 else 0).getbbox() or (0, 0, canvas.width, canvas.height)
    radius = max(12, round(0.022 * max(box[2] - box[0], box[3] - box[1])))
    cx, cy = box[0] + radius * 1.4, box[1] + radius * 1.4
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((cx - radius - 4, cy - radius - 4, cx + radius + 4, cy + radius + 4), fill=(255, 255, 255, 255))
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=rgb + (255,))
    buffer = io.BytesIO()
    if path.suffix.lower() == '.png':
        canvas.save(buffer, 'PNG')
        prefix = 'data:image/png;base64,'
    else:
        canvas.convert('RGB' if mode != 'L' else 'RGB').save(buffer, 'JPEG', quality=90)
        prefix = 'data:image/jpeg;base64,'
    return prefix + base64.b64encode(buffer.getvalue()).decode()
