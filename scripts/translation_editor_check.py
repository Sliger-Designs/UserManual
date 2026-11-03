#!/usr/bin/env python3
"""Check a built translation editor against the real manual build.

1. English preview: every page's text, element structure and image/accessibility labels
   must equal the English build.
2. Round trip: pseudo-translate every item in the editor, export its ZIP, validate it with
   translation_package.py, rebuild the manuals from it, and compare with the editor preview.
"""
import argparse
import base64
import json
from pathlib import Path
import shutil
import tempfile

from playwright.sync_api import sync_playwright

from manual_build import build
from manual_localization import PackageLocalizer
from manual_paths import ROOT
from translation_memory import MemoryLocalizer, import_package
from translation_package import extract_package, protected_terms, validate
from translation_segments import needs_translation, segment_markdown

PAGES = '''(root) => [...root.querySelectorAll('.page')].map(page => ({
  id: page.id,
  text: page.textContent.replace(/\\s+/g, ' ').trim(),
  tags: [...page.querySelectorAll('*')].map(node => node.tagName.toLowerCase()).filter(tag => tag !== 'br').join(','),
  labels: [...page.querySelectorAll('[alt],[aria-label]')].map(node =>
    (node.getAttribute('alt') || '') + '|' + (node.getAttribute('aria-label') || '')).join(';'),
}))'''

# Accent letters outside protected text; keeps length similar so layouts still fit.
PSEUDO = '''() => {
  const editor = window.translationEditor, accents = {a: 'á', e: 'é', i: 'í', o: 'ö', u: 'ü', A: 'Á', E: 'É', O: 'Ö', U: 'Ü', n: 'ñ', c: 'ç'};
  for (const unit of editor.UNITS.values()) {
    if (!unit.needs) continue;
    const ranges = editor.tokenRanges(unit.english);
    let out = '', position = 0;
    for (const [start, end] of [...ranges, [unit.english.length, unit.english.length]]) {
      out += unit.english.slice(position, start).replace(/[aeiouAEOUnc]/g, c => accents[c]) + unit.english.slice(start, end);
      position = end;
    }
    editor.state.tm[unit.english] = out;
  }
  Object.assign(editor.state.job, {target_language: 'de', target_language_name: 'Pseudo', translator: 'self-test'});
  return editor.renderPreviews();
}'''


def compare(label, ours, theirs):
    failures = []
    if len(ours) != len(theirs):
        return [f'{label}: {len(ours)} pages, expected {len(theirs)}']
    for a, b in zip(ours, theirs):
        for key in ('text', 'tags', 'labels'):
            if a[key] != b[key]:
                at = next((k for k, (x, y) in enumerate(zip(a[key], b[key])) if x != y), min(len(a[key]), len(b[key])))
                failures.append(f'{label} {a["id"]} {key}:\n  editor: …{a[key][max(0, at - 60):at + 80]}\n  build:  …{b[key][max(0, at - 60):at + 80]}')
    return failures


def pages_of(browser, html):
    page = browser.new_page()
    page.set_content(html, wait_until='load')
    result = page.evaluate(f'() => ({PAGES})(document)')
    page.close()
    return result


def check(editor_path, browser_path, keep_zip=None, package_dir=None):
    package_name = editor_path.parent.name
    package_dir = package_dir or ROOT / 'translation-packages' / package_name
    manifest = json.loads((package_dir / 'manifest.json').read_text(encoding='utf-8'))
    models = manifest['models']
    spec = protected_terms(models)  # The rules the editor uses (see translation_editor.py).
    # Playwright sessions cannot nest, so build first, then drive the editor, then compare.
    english = {model: build(model, browser_path, html_only=True) for model in models}
    failures, errors, editor = [], [], {}
    with tempfile.TemporaryDirectory() as temporary:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=browser_path, headless=True)
            page = browser.new_page(viewport={'width': 1600, 'height': 1000})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
            page.goto(editor_path.as_uri())
            page.wait_for_function('window.translationEditor && !document.getElementById("preview-loading")', timeout=120000)
            preview = lambda model: page.evaluate(f'() => ({PAGES})(window.translationEditor.previews[{json.dumps(model)}].doc)')
            page.evaluate('() => document.querySelector(".toggle [data-mode=english]").click()')
            page.wait_for_timeout(1000)
            editor['English'] = {model: preview(model) for model in models}
            page.evaluate('() => document.querySelector(".toggle [data-mode=translated]").click()')
            page.evaluate(PSEUDO)
            editor['Translated'] = {model: preview(model) for model in models}
            # The build's segmenter must split Markdown exactly like the editor (same memory keys).
            js = page.evaluate('''() => ({
                files: Object.fromEntries(window.translationEditor.MD.map(file => [file.path, file.seg])),
                needs: Object.fromEntries([...window.translationEditor.UNITS.values()].map(unit => [unit.english, unit.needs])),
            })''')
            sources = {name: (package_dir / 'source/content/en' / Path(name).relative_to('content/en')).read_text(encoding='utf-8')
                       for name in manifest['markdown_files']}
            failures += [f'Segmentation differs from the editor: {name}' for name, text in sources.items()
                         if json.loads(json.dumps(segment_markdown(text, models))) != js['files'][name]]
            failures += [f'needs_translation differs from the editor: {english!r}' for english, needs in js['needs'].items()
                         if needs_translation(english, spec) != needs]
            # Protected-text rules: the pseudo-translation keeps every token; broken copies must be caught.
            failures += [f'Editor flags a valid translation: {item}' for item in page.evaluate('''() => {
                const editor = window.translationEditor;
                return [...editor.UNITS.values()].filter(unit => unit.needs && editor.tokenProblems(unit.english, editor.state.tm[unit.english]).length)
                    .map(unit => unit.english);
            }''')]
            failures += [f'Editor misses a broken translation: {item}' for item in page.evaluate('''() => {
                const editor = window.translationEditor, missed = [];
                for (const unit of editor.UNITS.values()) {
                    const tokens = editor.tokenRanges(unit.english);
                    if (!tokens.length) continue;
                    const [start, end] = tokens[0];
                    if (!editor.tokenProblems(unit.english, unit.english.slice(0, start) + unit.english.slice(end)).length) missed.push(unit.english);
                }
                return missed;
            }''')]
            failures += [f'Editor layout check: {issue}' for issue in page.evaluate(
                '() => Object.values(window.translationEditor.previews).flatMap(p => p.issues.map(i => p.model + " " + i.message))')]
            archive = Path(temporary) / f'{package_name}-de-translation.zip'
            archive.write_bytes(base64.b64decode(page.evaluate('''async () => {
                const editor = window.translationEditor, bytes = new Uint8Array(await editor.makeZip(editor.packageFiles()).arrayBuffer());
                let binary = ''; for (let i = 0; i < bytes.length; i += 32768) binary += String.fromCharCode(...bytes.subarray(i, i + 32768));
                return btoa(binary);
            }''')))
            browser.close()
        if keep_zip:
            shutil.copyfile(archive, keep_zip)
        package = extract_package(archive, Path(temporary) / 'returned')
        validate(package, complete=True, baseline=package_dir)
        localizer = PackageLocalizer(package)
        translated = {model: build(model, browser_path, localizer=localizer, html_only=True) for model in models}
        # Importing into a language memory and building from it must give the same manuals.
        memory_root = Path(temporary) / 'translations'
        import_package(archive, memory_root)
        for model in models:
            from_memory = MemoryLocalizer('de', memory_root)
            if build(model, browser_path, localizer=from_memory, html_only=True) != translated[model]:
                failures.append(f'Build from translation memory differs from build from package: {model}')
            failures += [f'Translation memory {model}: {line}' for line in from_memory.report()]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_path, headless=True)
        for label, built in (('English', english), ('Translated', translated)):
            for model in models:
                failures += compare(f'{label} {model}', editor[label][model], pages_of(browser, built[model]))
        browser.close()
    failures += [f'Browser error: {error}' for error in errors]
    for failure in failures:
        print('FAIL:', failure)
    if failures:
        raise SystemExit(f'{len(failures)} editor check failures')
    print(f'PASS: editor preview matches the build in English and after a validated pseudo-translation round trip ({", ".join(models)})')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('editor', type=Path, help='Built editor, e.g. _build/translation-editor/S630-S640-v1.0-en/index.html')
    parser.add_argument('--browser', default=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('chrome'),
                        help='Chromium executable (default: one on PATH, else Playwright''s bundled Chromium)')
    parser.add_argument('--keep-zip', type=Path, help='Save the pseudo-translated package ZIP here')
    parser.add_argument('--package', type=Path, help='Package the editor was built from (default: translation-packages/<editor folder name>)')
    args = parser.parse_args()
    check(args.editor.resolve(), args.browser, args.keep_zip and args.keep_zip.resolve(), args.package and args.package.resolve())


if __name__ == '__main__':
    main()
