#!/usr/bin/env python3
"""Build the web translation editor for a translation package.

The editor page holds the package's English text plus preview templates produced by the
real manual build (with placeholders in place of every translatable text), so its live
preview and printed PDF use the same layout, images, fonts and checks as `build_manual.py`.
Images and fonts are separate files named by content hash in a folder shared by every
editor (`assets/` beside the editor folders), so each is downloaded once and cached.
The editor runs from a web server (the Pages site, or `python -m http.server` locally).
"""
import argparse
import base64
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil

from manual_build import build, markdown_environment
from manual_localization import RecordingLocalizer, TokenLocalizer
from manual_paths import ROOT
from translation_package import TRANSLATION_FORMAT, handoff_readme, protected_terms
from translation_segments import segment_markdown, segments

EDITOR = ROOT / 'templates/translation-editor'
STATEMENT = re.compile(r"{%\s*(?:(?:if|elif) model [=!]= '[A-Za-z0-9]+'|else|endif)\s*%}")
DATA_URI = re.compile(r'data:([a-z]+/[a-z0-9.+-]+);base64,([A-Za-z0-9+/=]+)')
EXTENSIONS = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/svg+xml': '.svg', 'image/webp': '.webp',
              'font/woff2': '.woff2', 'font/woff': '.woff', 'font/ttf': '.ttf', 'font/otf': '.otf'}
# Where translators return their translation file (see templates/translation-editor/editor.js).
REPOSITORY = os.environ.get('GITHUB_REPOSITORY') or 'Sliger-Designs/UserManual'
RETURN_EMAIL = ''


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


def build_editor(package, browser, output, home_url=None, assets=None):
    """home_url: link the logo and an "All manuals" button to the manuals index (site builds only).
    assets: folder for the shared image/font files (default: `assets/` beside the editor's folder)."""
    import manual_build
    package = package.resolve()
    assets = (assets or output.parent.parent / 'assets').resolve()
    assets_url = Path(os.path.relpath(assets, output.parent.resolve())).as_posix()
    manifest = read_json(package / 'manifest.json')
    catalog = read_json(package / 'source/strings.json')
    markdown_files = []
    for name in manifest['markdown_files']:
        relative = Path(name).relative_to('content/en').as_posix()
        markdown_files.append({'path': name, 'file': 'translation/content/' + relative,
                               'text': (package / 'source/content/en' / relative).read_text(encoding='utf-8')})
    check_sources(manifest, catalog, markdown_files)
    terminology = package / 'terminology.md'
    # Current instructions (the package README is the snapshot from its export).
    instructions = handoff_readme(manifest['models'], manifest['source_version'], protected_terms(manifest['models']),
                                  manual_build.family(manifest['models'][0]))

    asset_urls, written = [], {}

    def stash(match):
        data = base64.b64decode(match.group(2))
        name = hashlib.sha256(data).hexdigest()[:24] + (EXTENSIONS.get(match.group(1)) or mimetypes.guess_extension(match.group(1)) or '.bin')
        if name not in written:
            written[name] = len(asset_urls)
            asset_urls.append(f'{assets_url}/{name}')
            target = assets / name
            if not target.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        return f'@@ASSET-{written[name]}@@'

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
        'schema': 2,
        'format': TRANSLATION_FORMAT,
        'package': {'name': package.name, 'models': manifest['models'],
                    'source_version': manifest['source_version'], 'source_commit': manifest['source_commit'],
                    'source_versions': manifest.get('source_versions') or {model: manifest['source_version'] for model in manifest['models']}},
        'instructions': instructions,
        'terminology': terminology.read_text(encoding='utf-8') if terminology.is_file() else '',
        'return': {'issue_url': f'https://github.com/{REPOSITORY}/issues/new', 'issue_template': 'translation-return.yml',
                   'email': RETURN_EMAIL},
        'strings': catalog,
        'markdown': markdown_files,
        'pages': read_json(package / 'page-map.json'),
        'expressions': placeholder_values,
        'templates': templates,
        'assets': asset_urls,
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
                         ('__HOME_OPEN__', f'<a class="home-link" href="{home_url}" title="Back to all manuals">' if home_url else ''),
                         ('__HOME_CLOSE__', '</a>' if home_url else ''),
                         ('__HOME_BUTTON__', f'<a class="button" href="{home_url}" title="Back to the list of all manuals">&larr; All manuals</a>' if home_url else ''),
                         ('__EDITOR_DATA__', data)]:
        assert page.count(marker) == 1, marker
        page = page.replace(marker, text)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding='utf-8')
    size = sum((assets / name).stat().st_size for name in written)
    print(f'Built {output} ({output.stat().st_size / 1e6:.1f} MB, plus {len(written)} images/fonts, '
          f'{size / 1e6:.1f} MB, in {assets}): {len(catalog)} strings, {len(markdown_files)} Markdown files; '
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
