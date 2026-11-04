"""Shared locations: lowercase category folders, original chassis/SKU casing."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_CATEGORIES = {
    'CX3150a': '3u',
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
    'S630': 'desktop',
    'S640': 'desktop',
}


def content_directory(model, language='en'):
    return ROOT / 'content' / language / MODEL_CATEGORIES[model] / model
