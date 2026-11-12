"""Shared locations: lowercase category folders, original chassis/SKU casing."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_CATEGORIES = {
    'CX2177a': '2u',
    'CX2177c': '2u',
    'CX2177x': '2u',
    'CX3150a': '3u',
    'CX3150i': '3u',
    'CX3150x': '3u',
    'CX3151a': '3u',
    'CX3151i': '3u',
    'CX3151x': '3u',
    'CX3152a': '3u',
    'CX3152i': '3u',
    'CX3170a': '3u',
    'CX3171a': '3u',
    'CX3172a': '3u',
    'CX3701': '3u',
    'CX3702': '3u',
    'CX3170aXL': '3u',
    'CX3170iXL': '3u',
    'CX3171aXL': '3u',
    'CX3171iXL': '3u',
    'CX3172aXL': '3u',
    'CX3172iXL': '3u',
    'CX4150a': '4u',
    'CX4150e': '4u',
    'CX4150i': '4u',
    'CX4170a': '4u',
    'CX4170e': '4u',
    'CX4170i': '4u',
    'CX4200a': '4u',
    'CX4200e': '4u',
    'CX4200f': '4u',
    'CX4200i': '4u',
    'CX4712': '4u',
    'CX4713': '4u',
    'S630': 'desktop',
    'S640': 'desktop',
}


# Repo model IDs have no spaces. Where the catalog SKU (and the supplied render folder) differs,
# e.g. "CX3170a XL", it is listed here; the website slug follows it ("cx3170a_xl").
CATALOG_NAMES = {'CX3170aXL': 'CX3170a XL', 'CX3170iXL': 'CX3170i XL', 'CX3171aXL': 'CX3171a XL', 'CX3171iXL': 'CX3171i XL', 'CX3172aXL': 'CX3172a XL', 'CX3172iXL': 'CX3172i XL'}


def catalog_name(model):
    return CATALOG_NAMES.get(model, model)


def web_slug(model):
    return catalog_name(model).lower().replace(' ', '_')


def originals_directory(model):
    return ROOT / 'illustrations' / MODEL_CATEGORIES[model] / catalog_name(model)


def content_directory(model, language='en'):
    return ROOT / 'content' / language / MODEL_CATEGORIES[model] / model


PUBLISHED = ROOT / 'illustrations' / 'published'


def published_directory(model):
    """Publication copies, manifest.json and inventory.json: published/<category>/<model>/ ('common' for shared assets)."""
    return PUBLISHED / 'common' if model == 'common' else PUBLISHED / MODEL_CATEGORIES[model] / model


def inventory_path(model):
    """Inventory of a model's supplied originals ('common' for shared originals)."""
    return published_directory(model) / 'inventory.json'


REFERENCE_INVENTORY = PUBLISHED / 'common' / 'reference-inventory.json'
