"""Shift one hue band of a render toward the manual's standard part colour (e.g. a pale tan
bracket toward the orange used in the other renders). Pixels outside the band (white, grey,
screws, other parts) are unchanged; a soft edge on the hue and saturation limits avoids seams."""
import numpy as np
from PIL import Image

EDGE_DEGREES = 4.0
EDGE_SATURATION = 0.15


def shift_hue_band(image, hue_range_deg, hue_shift_deg, saturation_scale, value_scale, min_saturation=0.15):
    low, high = hue_range_deg
    assert 0 <= low < high <= 360 and -30 <= hue_shift_deg <= 30
    assert 0.5 <= saturation_scale <= 2 and 0.5 <= value_scale <= 1.5
    hsv = np.asarray(image.convert('RGB').convert('HSV')).astype(np.float32)
    hue, saturation, value = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    weight = (np.clip((hue - (low - EDGE_DEGREES)) / EDGE_DEGREES, 0, 1)
              * np.clip(((high + EDGE_DEGREES) - hue) / EDGE_DEGREES, 0, 1)
              * np.clip((saturation - min_saturation) / EDGE_SATURATION, 0, 1))
    hue = (hue + hue_shift_deg * weight) % 360
    saturation = np.clip(saturation * (1 + (saturation_scale - 1) * weight), 0, 1)
    value = np.clip(value * (1 + (value_scale - 1) * weight), 0, 1)
    out = np.stack([hue * 255 / 360, saturation * 255, value * 255], -1).round().clip(0, 255).astype(np.uint8)
    adjusted = Image.fromarray(out, 'HSV').convert('RGB')
    return adjusted, {
        'hue_range_deg': list(hue_range_deg), 'hue_shift_deg': hue_shift_deg,
        'saturation_scale': saturation_scale, 'value_scale': value_scale, 'min_saturation': min_saturation,
        'pixels_adjusted': int((weight > 0).sum()), 'total_pixels': int(weight.size),
        'method': 'HSV shift of pixels inside the hue band, weighted by a soft edge on hue and saturation; other pixels unchanged.',
    }
