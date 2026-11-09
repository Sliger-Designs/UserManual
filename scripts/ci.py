#!/usr/bin/env python3
"""Continuous-integration and publishing tasks, used by .github/workflows/ and runnable locally.

  plan           which manuals, translations and packages a set of changed files affects
  check          build and validate what a plan lists; collect PDFs and a summary
  site           build the GitHub Pages site: editors, preview PDFs, released PDFs
                 (--reuse takes the PDFs `check` already built for the same commit)
  import-issue   import a translation file attached to an issue into translations/<lang>/
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import contextlib
from datetime import datetime, timezone
from html import escape
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import traceback
import urllib.request

import manual_build
from manual_localization import RecordingLocalizer
from manual_assets import released_versions
from manual_paths import MODEL_CATEGORIES, ROOT, content_directory, published_directory

# Changes here can affect every manual (and every translation package's editor).
GLOBAL_PREFIXES = ('scripts/', 'templates/', 'glossary/', 'products/shared/', 'illustrations/published/common/',
                   'illustrations/published/covers/', 'sources/original/', 'requirements.txt', '.github/workflows/')
# The editor's translation file (.json); older editors returned a ZIP.
ATTACHMENT = re.compile(r'https://github\.com/(?:user-attachments/files|[\w.-]+/[\w.-]+/files)/\d+/[^\s)\]>"\']+?\.(?:json|zip)')
MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024


def languages():
    return sorted(path.parent.name for path in (ROOT / 'translations').glob('*/memory.json'))


def packages():
    return sorted(path.parent.name for path in (ROOT / 'translation-packages').glob('*/manifest.json'))


def current_packages():
    """Packages translators use: those not replaced by a newer export
    (translation-packages/superseded.json maps old -> new). Only these get an editor."""
    superseded = ROOT / 'translation-packages/superseded.json'
    old = json.loads(superseded.read_text(encoding='utf-8')) if superseded.is_file() else {}
    return [name for name in packages() if name not in old]


def model_inputs(model):
    """Markdown files the model's build reads (recorded, not guessed) and its own data folders."""
    recorder = RecordingLocalizer()
    recorder.model = model
    manual_build.build(model, None, localizer=recorder, render_only=True)
    folders = (content_directory(model).relative_to(ROOT).as_posix() + '/', f'products/{model}.json',
               published_directory(model).relative_to(ROOT).as_posix() + '/', f'releases/en/{MODEL_CATEGORIES[model]}/{model}/')
    return set(recorder.markdown_files), folders


def plan(changed=None):
    """What to build. `changed=None` means everything (pushes to main, manual runs)."""
    if changed is None:
        return {'models': sorted(MODEL_CATEGORIES), 'languages': {lang: {'models': sorted(MODEL_CATEGORIES), 'required': False}
                                                                   for lang in languages()}, 'packages': packages()}
    changed = [path.replace('\\', '/') for path in changed if path.strip()]
    everything = any(path.startswith(GLOBAL_PREFIXES) for path in changed)
    models = set()
    for model in MODEL_CATEGORIES:
        markdown, folders = model_inputs(model)
        if everything or any(path in markdown or path.startswith(folders) for path in changed):
            models.add(model)
    result_languages = {}
    for lang in languages():
        touched = any(path.startswith(f'translations/{lang}/') for path in changed)
        targets = sorted(MODEL_CATEGORIES) if touched else sorted(models)
        if targets:
            result_languages[lang] = {'models': targets, 'required': touched}
    tooling = any(path.startswith(('scripts/', 'templates/', 'glossary/', '.github/workflows/')) for path in changed)
    result_packages = [name for name in packages()
                       if tooling or any(path.startswith(f'translation-packages/{name}/') for path in changed)]
    return {'models': sorted(models), 'languages': result_languages, 'packages': result_packages}


class Results:
    """Collects outcomes, copies outputs and writes a Markdown summary."""

    def __init__(self, output):
        self.output, self.rows, self.failed = output, [], False
        output.mkdir(parents=True, exist_ok=True)

    def run(self, kind, name, action, required=True):
        print(f'\n=== {kind}: {name}', flush=True)
        try:
            self.record(kind, name, None, action() or 'passed')
        except BaseException as error:  # SystemExit from check scripts, assertions from builds
            if isinstance(error, KeyboardInterrupt):
                raise
            traceback.print_exc()
            self.record(kind, name, error_message(error), required=required)

    def record(self, kind, name, error, detail='passed', required=True):
        if error is None:
            self.rows.append((kind, name, '✅', detail))
        else:
            self.rows.append((kind, name, '❌' if required else '⚠️', escape(error)[:300]))
            self.failed |= required

    def keep(self, outputs, folder):
        target = self.output / folder
        target.mkdir(parents=True, exist_ok=True)
        for key in ('pdf', 'overview', 'report'):
            if outputs and outputs.get(key) and Path(outputs[key]).is_file():
                shutil.copy2(outputs[key], target / Path(outputs[key]).name)

    def summary(self, title):
        lines = [f'## {title}', '', '| Check | Item | Result | Details |', '|---|---|---|---|']
        lines += [f'| {kind} | {name} | {mark} | {detail} |' for kind, name, mark, detail in self.rows]
        if not self.rows:
            lines.append('| — | — | ✅ | Nothing to build for these changes |')
        lines += ['', 'PDFs, page overviews and validation reports are in the run artifact.']
        text = '\n'.join(lines) + '\n'
        (self.output / 'summary.md').write_text(text, encoding='utf-8')
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as summary:
                summary.write(text)
        print('\n' + text)


def build_translation(model, language):
    """Build a translated manual if its memory is complete; otherwise report the gaps."""
    from translation_memory import MemoryLocalizer
    dry = MemoryLocalizer(language)
    manual_build.build(model, None, localizer=dry, render_only=True)
    if dry.report():
        raise ValueError(f'{len(dry.missing)} missing, {len(dry.problems)} invalid texts in translations/{language}')
    return manual_build.build(model, None, localizer=MemoryLocalizer(language))


def error_message(error):
    message = (str(error) or type(error).__name__).strip().splitlines()
    return message[-1] if message else 'failed'


def build_manual(model, language, browser=None):
    """Build one manual (in a worker process). Returns (output paths or None, error or None, log)."""
    log = io.StringIO()
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        try:
            built = manual_build.build(model, browser) if language == 'en' else build_translation(model, language)
            return {key: str(built[key]) for key in ('pdf', 'overview', 'report') if built.get(key)}, None, log.getvalue()
        except BaseException as error:  # SystemExit from check scripts, assertions from builds
            if isinstance(error, KeyboardInterrupt):
                raise
            traceback.print_exc()
            return None, error_message(error), log.getvalue()


def build_manuals(jobs, browser=None):
    """Build (model, language) pairs in parallel: one process (and Chromium) per CPU core, or
    $CI_JOBS. Yields (job, outputs, error) in the order given, printing each build's log whole."""
    if not jobs:
        return
    workers = min(int(os.environ.get('CI_JOBS') or 0) or os.cpu_count() or 1, len(jobs))
    print(f'Building {len(jobs)} manuals with {workers} workers', flush=True)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(build_manual, model, language, browser) for model, language in jobs]
        for (model, language), future in zip(jobs, futures):
            outputs, error, log = future.result()
            print(f'\n=== {language} manual: {model}\n{log}', end='', flush=True)
            yield (model, language), outputs, error


def check(the_plan, output, browser=None):
    from translation_editor import build_editor
    from translation_editor_check import check as check_editor
    from translation_package import validate
    results = Results(output)
    # Publish site reuses these PDFs; the plan tells it which builds ran (a missing PDF means it failed).
    (output / 'plan.json').write_text(json.dumps(the_plan, indent=2), encoding='utf-8')
    jobs = [(model, 'en') for model in the_plan['models']]
    jobs += [(model, language) for language, item in the_plan['languages'].items() for model in item['models']]
    for (model, language), outputs, error in build_manuals(jobs, browser):
        if outputs:
            results.keep(outputs, f'{language}/{model}')
        results.record('English manual' if language == 'en' else f'{language} manual', model, error,
                       required=language == 'en' or the_plan['languages'][language]['required'])
    for name in the_plan['packages']:
        package = ROOT / 'translation-packages' / name
        results.run('Translation package', name, lambda: validate(package))
        if name not in current_packages():
            continue

        def editor():
            try:
                path = build_editor(package, browser, output / 'editors' / name / 'index.html')
            except ValueError as error:
                if 'English content changed' in str(error):
                    return 'skipped: English changed since this package was exported (expected for older packages)'
                raise
            check_editor(path, browser, package_dir=package)
            return 'preview matches build; round trip validated'
        results.run('Translation editor', name, editor)
    results.summary('Manual checks')
    return not results.failed


FORM_FACTORS = {'desktop': 'Desktop', '2u': '2U rackmount', '3u': '3U rackmount', '4u': '4U rackmount'}
LANGUAGE_CODES = ['bg', 'cs', 'da', 'de', 'el', 'es', 'et', 'fi', 'fr', 'ga', 'hr', 'hu', 'it', 'lt', 'lv', 'mt', 'nl',
                  'no', 'pl', 'pt', 'ro', 'sk', 'sl', 'sv', 'tr', 'uk']


def site(output, browser=None, reuse=None):
    """Static site for GitHub Pages: a generated list of every manual with its PDFs and
    translation choices (templates/site/index.html), one translation editor per package
    (all languages inside), preview PDFs of main and released PDFs.
    `reuse` is the output of `check` for the same commit: its PDFs are used as they are, and
    only what its plan left out is built."""
    import base64
    from translation_editor import build_editor
    from translation_memory import Memory, coverage
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    site_packages = {}
    for name in current_packages():
        package = ROOT / 'translation-packages' / name
        manifest = json.loads((package / 'manifest.json').read_text(encoding='utf-8'))
        try:
            build_editor(package, browser, output / 'editors' / name / 'index.html', home_url='../../index.html')
            editor = f'editors/{name}/index.html'
        except ValueError as error:  # English changed since the package was exported.
            print(f'No editor for {name}: {str(error).splitlines()[0]}')
            editor = None
        site_packages[name] = {'editor': editor, 'commit': manifest['source_commit'], 'models': manifest['models'],
                               'version': manifest['source_version']}

    released = {}
    for pdf in sorted((ROOT / 'releases').rglob('*.pdf')):
        relative = pdf.relative_to(ROOT / 'releases')
        language, _, model, revision = relative.parts[:4]
        target = output / 'manuals/released' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, target)
        released.setdefault(model, []).append((language, revision, f'manuals/released/{relative.as_posix()}'))

    order = list(FORM_FACTORS)
    models = sorted(MODEL_CATEGORIES, key=lambda sku: (order.index(MODEL_CATEGORIES[sku]), sku))
    checked = json.loads((reuse / 'plan.json').read_text(encoding='utf-8')) if reuse and (reuse / 'plan.json').is_file() else None
    attempted = set()
    if checked:
        attempted = {(model, 'en') for model in checked['models']}
        attempted |= {(model, language) for language, item in checked['languages'].items() for model in item['models']}
    previews, to_build = {}, []
    for model in models:
        for language in ['en'] + languages():
            if (model, language) not in attempted:
                to_build.append((model, language))
            elif pdf := next((reuse / language / model).glob('*.pdf'), None):
                previews[model, language] = (pdf, next((reuse / language / model).glob('*-validation.json'), None))
            else:
                print(f'No {language} preview for {model}: it did not build in Manual checks')
    print(f'Reusing {len(previews)} PDFs from Manual checks; building {len(to_build)}', flush=True)
    for (model, language), outputs, error in build_manuals(to_build, browser):
        if error:
            print(f'No {language} preview for {model}: {error}')
        else:
            previews[model, language] = (Path(outputs['pdf']), Path(outputs['report']) if outputs.get('report') else None)

    manuals = []
    for model in models:
        manual = manual_build.manual(model)
        pdfs = [{'label': f'{language} · {revision}', 'note': 'Released', 'href': href}
                for language, revision, href in sorted(released.get(model, []))]
        # A released manual lists its English preview only while main has unreleased changes.
        releases_of_model = released_versions(model, MODEL_CATEGORIES[model])
        latest = releases_of_model[-1] if releases_of_model else None
        if latest and (model, 'en') in previews:
            report = previews[model, 'en'][1]
            fingerprint = json.loads(report.read_text(encoding='utf-8')).get('content_fingerprint') if report else None
            if fingerprint == latest['content_fingerprint']:
                del previews[model, 'en']
        preview_links = {}
        for language in ['en'] + languages():
            if (model, language) not in previews:
                continue
            target = output / 'manuals/preview' / language / f'{model}.pdf'
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(previews[model, language][0], target)
            preview_links[language] = f'manuals/preview/{language}/{model}.pdf'
        if 'en' in preview_links and latest:
            pdfs.append({'label': f'en · {manual["revision"]} draft', 'note': f'Unreleased changes since {latest["revision"]}; not a release',
                         'href': preview_links['en']})
        elif 'en' in preview_links:
            pdfs.append({'label': f'en · {manual["revision"]} preview', 'note': 'Current text on main; not a release', 'href': preview_links['en']})
        candidates = [name for name, item in site_packages.items() if model in item['models'] and item['editor']]
        model_languages = {}
        for language in languages():
            done, total = coverage(language, model)
            model_languages[language] = {'name': Memory(language).language_name, 'done': done, 'total': total,
                                         'preview': preview_links.get(language)}
        manuals.append({'model': model, 'display_name': manual.get('display_name', model), 'revision': manual['revision'], 'released': bool(manual.get('release_ready')),
                        'description': ' · '.join(filter(None, [manual.get('cover_description', ''), *([manual['cover_description_detail']] if isinstance(manual.get('cover_description_detail'), str) else manual.get('cover_description_detail', []))])), 'form_factor': FORM_FACTORS.get(MODEL_CATEGORIES[model], ''),
                        'pdfs': pdfs, 'package': candidates[-1] if candidates else None, 'languages': model_languages})

    data = {'manuals': manuals, 'packages': site_packages, 'language_codes': LANGUAGE_CODES,
            'built': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
            'commit': (os.environ.get('SITE_COMMIT') or os.environ.get('GITHUB_SHA', ''))[:7] or 'local'}
    page = (ROOT / 'templates/site/index.html').read_text(encoding='utf-8')
    logo = 'data:image/svg+xml;base64,' + base64.b64encode((ROOT / 'templates/brand/sliger-logo.svg').read_bytes()).decode()
    for marker, text in [('/*__WORKSPACES_JS__*/', (ROOT / 'templates/translation-editor/workspaces.js').read_text(encoding='utf-8')),
                         ('__SLIGER_LOGO__', logo),
                         ('__SITE_DATA__', json.dumps(data, ensure_ascii=False).replace('<', '\u003c'))]:
        assert page.count(marker) == 1, marker
        page = page.replace(marker, text)
    (output / 'index.html').write_text(page, encoding='utf-8')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Site in {output}: {len(manuals)} manuals, {sum(1 for item in site_packages.values() if item["editor"])} editors')


def import_issue(body, issue, output, browser=None):
    """Download the issue's attached translation file, import it and build what is complete.
    Writes import.json (for the workflow) and result.md (posted on the issue / PR)."""
    from translation_memory import import_package
    output.mkdir(parents=True, exist_ok=True)
    result_md = output / 'result.md'
    urls = ATTACHMENT.findall(body or '')
    if not urls:
        result_md.write_text('No translation file found. Drag the file downloaded from the translation editor '
                             '(…-translation.json) into the issue, then add the label again.\n', encoding='utf-8')
        raise SystemExit('No translation file attached to the issue')
    request = urllib.request.Request(urls[0], headers={'User-Agent': 'sliger-manual-ci'})
    if os.environ.get('GITHUB_TOKEN'):
        request.add_header('Authorization', 'token ' + os.environ['GITHUB_TOKEN'])
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / ('returned' + Path(urls[0]).suffix.lower())
        with urllib.request.urlopen(request, timeout=120) as response, open(archive, 'wb') as file:
            size = 0
            while chunk := response.read(1 << 20):
                size += len(chunk)
                if size > MAX_ATTACHMENT_BYTES:
                    raise SystemExit('Attachment is larger than 25 MB')
                file.write(chunk)
        try:
            imported = import_package(archive)
        except Exception as error:
            result_md.write_text(f'The translation could not be imported:\n\n```\n{error}\n```\n'
                                 'Fix it in the translation editor, download the translation file again and attach it.\n', encoding='utf-8')
            raise
    results = Results(output)
    for model in imported['models']:
        results.run(f'{imported["language"]} manual', model,
                    lambda: results.keep(build_translation(model, imported['language']), f'{imported["language"]}/{model}'), required=False)
    results.summary(f'Translation import from #{issue}')
    counts, job = imported['counts'], imported['job']
    lines = [f'Imports the **{job.get("target_language_name") or imported["language"]}** ({imported["language"]}) translation '
             f'from #{issue} (package `{imported["package"]}`) into `translations/{imported["language"]}/memory.json`.', '',
             f'- {counts["added"]} added, {counts["changed"]} changed, {counts["unchanged"]} unchanged entries',
             f'- Translator: {job.get("translator") or "not given"}; reviewer: {job.get("reviewer") or "not given"}']
    if imported['skipped']:
        lines.append('- Not imported (Markdown structure changed; translate in the editor): ' + ', '.join(imported['skipped']))
    if job.get('notes'):
        lines += ['', '**Translator notes**', '', '> ' + job['notes'].replace('\n', '\n> ')]
    lines += ['', (output / 'summary.md').read_text(encoding='utf-8'),
              'Review the `memory.json` diff and the PDFs in the import run artifact before merging. '
              'Built translations are not released manuals.']
    result_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (output / 'import.json').write_text(json.dumps({'language': imported['language'], 'package': imported['package']}), encoding='utf-8')
    return imported


def main():
    for stream in (sys.stdout, sys.stderr):  # Never fail on a console that cannot show ✅.
        stream.reconfigure(errors='replace')
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    planner = sub.add_parser('plan', help='Print a JSON build plan')
    planner.add_argument('--changed', type=Path, help='File listing changed paths, one per line (default: everything)')
    checker = sub.add_parser('check', help='Build and validate what a plan lists')
    checker.add_argument('--plan', type=Path, help='Plan JSON from `plan` (default: everything)')
    checker.add_argument('--output', type=Path, default=ROOT / '_build/ci')
    builder = sub.add_parser('site', help='Build the GitHub Pages site')
    builder.add_argument('--output', type=Path, default=ROOT / '_site')
    builder.add_argument('--reuse', type=Path, help='Output of `check` for the same commit; its PDFs are not rebuilt')
    importer = sub.add_parser('import-issue', help='Import a translation file attached to an issue (body from $ISSUE_BODY)')
    importer.add_argument('--issue', required=True)
    importer.add_argument('--output', type=Path, default=ROOT / '_build/ci')
    for command in (checker, builder, importer):
        command.add_argument('--browser', help="Chromium executable (default: Playwright's bundled Chromium)")
    args = parser.parse_args()
    if args.command == 'plan':
        changed = args.changed.read_text(encoding='utf-8-sig').splitlines() if args.changed else None
        print(json.dumps(plan(changed), indent=2))
    elif args.command == 'check':
        the_plan = json.loads(args.plan.read_text(encoding='utf-8')) if args.plan else plan()
        sys.exit(0 if check(the_plan, args.output.resolve(), args.browser) else 1)
    elif args.command == 'site':
        site(args.output.resolve(), args.browser, args.reuse.resolve() if args.reuse else None)
    else:
        import_issue(os.environ.get('ISSUE_BODY', ''), args.issue, args.output.resolve(), args.browser)


if __name__ == '__main__':
    main()
