#!/usr/bin/env python3
"""Build the single-file browser translation editor for a translation package.

The editor embeds the package's English text plus preview templates produced by the real
manual build (with placeholders in place of every translatable text), so its live preview
and printed PDF use the same layout, images, fonts and checks as `build_manual.py`.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil

from manual_build import build, markdown_environment
from manual_localization import RecordingLocalizer, TokenLocalizer
from manual_paths import ROOT
from translation_package import protected_terms
from translation_segments import segment_markdown, segments

EDITOR = ROOT / 'templates/translation-editor'
STATEMENT = re.compile(r"{%\s*(?:(?:if|elif) model [=!]= '[A-Za-z0-9]+'|else|endif)\s*%}")
DATA_URI = re.compile(r'data:([a-z]+/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_sources(manifest, catalog, markdown_files):
    """Preview templates come from the working tree: every text the build uses now must be in the package."""
    recorder = RecordingLocalizer()
    for model in manifest['models']:
        recorder.model = model
        build(model, None, localizer=recorder, render_only=True)
    known = {entry['source'] for entry in catalog.values()}
    sources = {item['path']: item['text'] for item in markdown_files}
    stale = [f'text not in package: {text!r}' for text in recorder.strings if text not in known]
    stale += [f'changed Markdown: {path}' for path, text in recorder.markdown_files.items() if sources.get(path) != text]
    if stale:
        raise ValueError('English content changed since this package was exported; export a new '
                         'package or check out its source commit:\n  ' + '\n  '.join(stale))


def expressions(models, markdown_files, localizer):
    """Pre-render each `{{ ... }}` placeholder per model, so the editor needs no Jinja engine.
    Text a placeholder prints (hardware references, link labels) becomes `@@S-...@@` tokens."""
    values = {}
    for model in models:
        env, context = markdown_environment(model, localizer)
        values[model] = {}
        for item in markdown_files:
            for statement in re.findall(r'{%.*?%}', item['text'], re.S):
                if not STATEMENT.fullmatch(statement):
                    raise ValueError(f'{item["path"]}: the editor does not support {statement}')
            for expression in re.findall(r'{{(.*?)}}', item['text'], re.S):
                try:
                    values[model][expression.strip()] = env.from_string(
                        '{{' + expression + '}}').render(**context)
                except Exception:  # A model-specific fact used only by the other model's file.
                    pass
    return values


def memories_for(catalog, markdown_files):
    """Each language memory's entries for this package's English text: the editor offers
    those languages and pre-fills them. Text only, a few KB per language."""
    from translation_memory import MEMORY_ROOT, Memory
    english = {entry['source'] for entry in catalog.values()}
    english |= {part['text'] for item in markdown_files for part in segments(segment_markdown(item['text']))}
    memories = {}
    for path in sorted(MEMORY_ROOT.glob('*/memory.json')):
        memory = Memory(path.parent.name)
        entries = {text: memory.translation(text) for text in sorted(english) if memory.translation(text) is not None}
        if entries:
            memories[memory.language] = {'language_name': memory.language_name, 'entries': entries,
                                         'version': hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]}
    return memories


def build_editor(package, browser, output):
    package = package.resolve()
    manifest = read_json(package / 'manifest.json')
    catalog = read_json(package / 'source/strings.json')
    markdown_files = []
    for name in manifest['markdown_files']:
        relative = Path(name).relative_to('content/en').as_posix()
        markdown_files.append({'path': name, 'file': 'translation/content/' + relative,
                               'text': (package / 'source/content/en' / relative).read_text(encoding='utf-8')})
    check_sources(manifest, catalog, markdown_files)
    # Every read-only text file is returned unchanged; reference PDFs stay with Sliger.
    files = {path.relative_to(package).as_posix(): path.read_text(encoding='utf-8')
             for path in sorted(package.rglob('*')) if path.is_file()
             and path.relative_to(package).parts[0] not in ('reference', 'translation')}

    assets, asset_ids = [], {}

    def stash(match):
        key = hashlib.sha256(match.group(0).encode()).hexdigest()
        if key not in asset_ids:
            asset_ids[key] = len(assets)
            assets.append({'type': match.group(1), 'data': match.group(2)})
        return f'@@ASSET-{asset_ids[key]}@@'

    localizer = TokenLocalizer(catalog, manifest['markdown_files'])
    templates, used = {}, set()
    for model in manifest['models']:
        html = build(model, browser, localizer=localizer, html_only=True)
        tokens = set(re.findall(r'@@(S-s_[0-9a-f]{16}|MD-\d+-[A-Z]\d*|LANG)@@', html))
        unknown = set(re.findall(r'@@([^@\s<>"]{1,40})@@', html)) - tokens
        assert not unknown, f'Unrecognized placeholders in {model}: {sorted(unknown)}'
        used |= tokens
        templates[model] = DATA_URI.sub(stash, html)
    placeholder_values = expressions(manifest['models'], markdown_files, localizer)
    used |= {token for values in placeholder_values.values() for value in values.values()
             for token in re.findall(r'@@(S-s_[0-9a-f]{16})@@', value)}
    unused = [entry['source'] for key, entry in catalog.items() if f'S-{key}' not in used]
    if unused:
        print('Note: strings not shown in either manual preview:', '; '.join(unused))

    payload = {
        'schema': 1,
        'package': {'name': package.name, 'models': manifest['models'],
                    'source_version': manifest['source_version'], 'source_commit': manifest['source_commit'],
                    'source_versions': manifest.get('source_versions') or {model: manifest['source_version'] for model in manifest['models']}},
        'files': files,
        'strings': catalog,
        'markdown': markdown_files,
        'pages': read_json(package / 'page-map.json'),
        'expressions': placeholder_values,
        'templates': templates,
        'assets': assets,
        'layout_check': (ROOT / 'scripts/manual_layout_check.js').read_text(encoding='utf-8'),
        # Current rules (a superset of any older package's): the editor warns about everything
        # a build from the translation memory would reject.
        'protected': protected_terms(manifest['models']),
        'memories': memories_for(catalog, markdown_files),
        'job': read_json(package / 'translation/job.json'),
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    page = (EDITOR / 'editor.html').read_text(encoding='utf-8')
    for marker, text in [('/*__EDITOR_CSS__*/', (EDITOR / 'editor.css').read_text(encoding='utf-8')),
                         ('/*__WORKSPACES_JS__*/', (EDITOR / 'workspaces.js').read_text(encoding='utf-8')),
                         ('/*__EDITOR_JS__*/', (EDITOR / 'editor.js').read_text(encoding='utf-8')),
                         ('__PACKAGE_NAME__', package.name),
                         ('__SLIGER_LOGO__', 'data:image/svg+xml;base64,' + base64.b64encode(
                             (ROOT / 'templates/brand/sliger-logo.svg').read_bytes()).decode()),
                         ('__EDITOR_DATA__', data)]:
        assert page.count(marker) == 1, marker
        page = page.replace(marker, text)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding='utf-8')
    print(f'Built {output} ({output.stat().st_size / 1e6:.1f} MB): {len(catalog)} strings, '
          f'{len(markdown_files)} Markdown files, {len(assets)} shared images/fonts; '
          f'languages with translations: {", ".join(payload["memories"]) or "none"}')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('package', type=Path, help='Translation package folder, e.g. translation-packages/S630-S640-v1.0-en')
    parser.add_argument('--output', type=Path, help='Default: _build/translation-editor/<package>/index.html')
    parser.add_argument('--browser', default=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('chrome'),
                        help="Chromium executable (default: one on PATH, else Playwright's bundled Chromium)")
    args = parser.parse_args()
    output = args.output or ROOT / '_build/translation-editor' / args.package.resolve().name / 'index.html'
    build_editor(args.package, args.browser, output.resolve())


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, AssertionError) as error:
        raise SystemExit(str(error)) from error
