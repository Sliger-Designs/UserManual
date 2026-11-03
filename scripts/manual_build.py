"""One entry point for every manual family.

Each family module (build_sff_manual, build_rackmount_manual) provides
`build(model, browser_path, public_preview=False, localizer=None, html_only=False, render_only=False)`
and `markdown_environment(model, localizer=None)`. Translation tools call these through this
module, so a new family only has to implement that interface."""
import importlib
import json

from manual_paths import MODEL_CATEGORIES, content_directory

FAMILIES = {'sff': 'build_sff_manual', 'rackmount': 'build_rackmount_manual'}


def manual(model):
    return json.loads((content_directory(model) / 'manual.json').read_text(encoding='utf-8'))


def family(model):
    if model not in MODEL_CATEGORIES:
        raise ValueError(f'Unknown model {model}; add it to scripts/manual_paths.py')
    return manual(model).get('family', 'rackmount')


def module(model):
    return importlib.import_module(FAMILIES[family(model)])


def build(model, browser_path, **options):
    return module(model).build(model, browser_path, **options)


def markdown_environment(model, localizer=None):
    return module(model).markdown_environment(model, localizer)
