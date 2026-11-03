"""Replace a known flat background color without resampling or redrawing pixels."""
from PIL import Image, ImageChops


def white_background(image, reference_rgb, tolerance):
    assert len(reference_rgb) == 3 and all(isinstance(value, int) and 0 <= value <= 255 for value in reference_rgb)
    assert isinstance(tolerance, int) and 0 <= tolerance <= 16
    original = image.convert('RGB')
    difference = ImageChops.difference(original, Image.new('RGB', original.size, tuple(reference_rgb)))
    red, green, blue = difference.split()
    distance = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    mask = distance.point(lambda value: 255 if value <= tolerance else 0)
    cleaned = original.copy()
    cleaned.paste((255, 255, 255), (0, 0), mask)
    return cleaned, {
        'reference_rgb': reference_rgb,
        'tolerance_per_channel': tolerance,
        'background_pixels_replaced': mask.histogram()[255],
        'total_pixels': original.width * original.height,
        'method': 'Replace only pixels within the specified distance of the flat background with RGB white; preserve all other source pixels exactly.',
    }
