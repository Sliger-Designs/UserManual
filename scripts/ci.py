#!/usr/bin/env python3
"""Continuous-integration and publishing tasks, used by .github/workflows/ and runnable locally.

  plan           which manuals, translations and packages a set of changed files affects
  check          build and validate what a plan lists; collect PDFs and a summary
  site           build the GitHub Pages site: editors, preview PDFs, released PDFs
  import-issue   import a translation ZIP attached to an issue into translations/<lang>/
"""
import argparse
from datetime import datetime, timezone
from html import escape
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
from manual_paths import MODEL_CATEGORIES, ROOT, content_directory

# Changes here can affect every manual (and every translation package's editor).
GLOBAL_PREFIXES = ('scripts/', 'templates/', 'glossary/', 'products/shared/', 'illustrations/published/common/',
                   'illustrations/published/covers/', 'sources/original/', 'requirements.txt', '.github/workflows/')
ATTACHMENT = re.compile(r'https://github\.com/(?:user-attachments/files|[\w.-]+/[\w.-]+/files)/\d+/[^\s)\]>"\']+?\.zip')
MAX_ZIP_BYTES = 100 * 1024 * 1024


def languages():
    return sorted(path.parent.name for path in (ROOT / 'translations').glob('*/memory.json'))


def packages():
    return sorted(path.parent.name for path in (ROOT / 'translation-packages').glob('*/manifest.json'))


def model_inputs(model):
    """Markdown files the model's build reads (recorded, not guessed) and its own data folders."""
    recorder = RecordingLocalizer()
    recorder.model = model
    manual_build.build(model, None, localizer=recorder, render_only=True)
    folders = (content_directory(model).relative_to(ROOT).as_posix() + '/', f'products/{model}.json',
               f'illustrations/published/{model}/', f'releases/en/{MODEL_CATEGORIES[model]}/{model}/')
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
            detail = action() or 'passed'
            self.rows.append((kind, name, '✅', detail))
        except BaseException as error:  # SystemExit from check scripts, assertions from builds
            if isinstance(error, KeyboardInterrupt):
                raise
            traceback.print_exc()
            message = (str(error) or type(error).__name__).strip().splitlines()
            self.rows.append((kind, name, '❌' if required else '⚠️', escape(message[-1] if message else 'failed')[:300]))
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


def check(the_plan, output, browser=None):
    from translation_editor import build_editor
    from translation_editor_check import check as check_editor
    from translation_package import validate
    results = Results(output)
    for model in the_plan['models']:
        results.run('English manual', model, lambda: results.keep(manual_build.build(model, browser), f'en/{model}'))
    for language, item in the_plan['languages'].items():
        for model in item['models']:
            results.run(f'{language} manual', model,
                        lambda: results.keep(build_translation(model, language), f'{language}/{model}'), required=item['required'])
    for name in the_plan['packages']:
        package = ROOT / 'translation-packages' / name
        results.run('Translation package', name, lambda: validate(package))

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


PAGE = '''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sliger manuals</title>
<style>
body{{font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#1d2327;margin:0;background:#f4f6f7}}
header{{background:white;border-bottom:1px solid #d9dee2;padding:18px 24px;display:flex;gap:14px;align-items:center}}
header img{{height:24px}} main{{max-width:960px;margin:0 auto;padding:12px 24px 60px}}
h2{{margin-top:32px;font-size:1.15em}} table{{border-collapse:collapse;width:100%;background:white}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid #e3e7ea}} th{{font-size:.8em;text-transform:uppercase;color:#5b6670}}
a{{color:#b92e32}} .note{{color:#5b6670;font-size:.9em}}
</style></head><body>
<header><img src="{logo}" alt="Sliger"><strong>User manuals</strong></header>
<main>{body}<p class="note">Built {built} from commit {commit}.</p></main></body></html>
'''


def site(output, browser=None):
    """Static site for GitHub Pages: translation editors, preview PDFs of main, released PDFs."""
    import base64
    from translation_editor import build_editor
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    sections = []

    editors = []
    for name in packages():
        package = ROOT / 'translation-packages' / name
        for language in [None] + languages():
            filename = f'index-{language}.html' if language else 'index.html'
            try:
                build_editor(package, browser, output / 'editors' / name / filename, language)
            except ValueError as error:
                print(f'Skipping editor {name} {language or ""}: {str(error).splitlines()[0]}')
                continue
            editors.append((name, language or 'new translation', f'editors/{name}/{filename}'))
    if editors:
        rows = ''.join(f'<tr><td>{escape(name)}</td><td>{escape(label)}</td><td><a href="{href}">Open editor</a></td></tr>'
                       for name, label, href in editors)
        sections.append('<h2>Translation editors</h2><p class="note">Work stays in your browser; download the ZIP from the '
                        'editor to send it to Sliger.</p><table><tr><th>Package</th><th>Language</th><th></th></tr>' + rows + '</table>')

    released = sorted((ROOT / 'releases').rglob('*.pdf'))
    for pdf in released:
        target = output / 'manuals/released' / pdf.relative_to(ROOT / 'releases')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, target)
    if released:
        rows = ''.join(f'<tr><td>{escape(pdf.parts[-3])}</td><td>{escape(pdf.relative_to(ROOT / "releases").parts[0])}</td>'
                       f'<td>{escape(pdf.parts[-2])}</td><td><a href="manuals/released/{pdf.relative_to(ROOT / "releases").as_posix()}">PDF</a></td></tr>'
                       for pdf in released)
        sections.append('<h2>Released manuals</h2><table><tr><th>Model</th><th>Language</th><th>Revision</th><th></th></tr>' + rows + '</table>')

    previews = []
    for model in sorted(MODEL_CATEGORIES):
        for language in ['en'] + languages():
            try:
                built = manual_build.build(model, browser) if language == 'en' else build_translation(model, language)
            except Exception as error:
                print(f'No {language} preview for {model}: {error}')
                continue
            target = output / 'manuals/preview' / language / f'{model}.pdf'
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(built['pdf'], target)
            revision = manual_build.manual(model)['revision']
            previews.append((model, language, revision, f'manuals/preview/{language}/{model}.pdf'))
    if previews:
        rows = ''.join(f'<tr><td>{escape(model)}</td><td>{escape(language)}</td><td>{escape(revision)}</td><td><a href="{href}">PDF</a></td></tr>'
                       for model, language, revision, href in previews)
        sections.append('<h2>Current previews</h2><p class="note">Built from the latest approved text on main. '
                        'Not released; for review only.</p><table><tr><th>Model</th><th>Language</th><th>Revision</th><th></th></tr>' + rows + '</table>')

    logo = 'data:image/svg+xml;base64,' + base64.b64encode((ROOT / 'templates/brand/sliger-logo.svg').read_bytes()).decode()
    commit = os.environ.get('GITHUB_SHA', '')[:7] or 'local'
    built = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    (output / 'index.html').write_text(PAGE.format(logo=logo, body=''.join(sections), built=built, commit=escape(commit)), encoding='utf-8')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Site in {output}: {len(editors)} editors, {len(released)} released and {len(previews)} preview PDFs')


def import_issue(body, issue, output, browser=None):
    """Download the issue's attached translation ZIP, import it and build what is complete.
    Writes import.json (for the workflow) and result.md (posted on the issue / PR)."""
    from translation_memory import import_package
    output.mkdir(parents=True, exist_ok=True)
    result_md = output / 'result.md'
    urls = ATTACHMENT.findall(body or '')
    if not urls:
        result_md.write_text('No translation ZIP found. Drag the ZIP downloaded from the translation editor into the issue, then add the label again.\n', encoding='utf-8')
        raise SystemExit('No ZIP attachment in the issue')
    request = urllib.request.Request(urls[0], headers={'User-Agent': 'sliger-manual-ci'})
    if os.environ.get('GITHUB_TOKEN'):
        request.add_header('Authorization', 'token ' + os.environ['GITHUB_TOKEN'])
    with tempfile.TemporaryDirectory() as temporary:
        archive = Path(temporary) / 'returned.zip'
        with urllib.request.urlopen(request, timeout=120) as response, open(archive, 'wb') as file:
            size = 0
            while chunk := response.read(1 << 20):
                size += len(chunk)
                if size > MAX_ZIP_BYTES:
                    raise SystemExit('Attachment is larger than 100 MB')
                file.write(chunk)
        try:
            imported = import_package(archive)
        except Exception as error:
            result_md.write_text(f'The translation could not be imported:\n\n```\n{error}\n```\n'
                                 'Fix it in the translation editor, download the ZIP again and attach it.\n', encoding='utf-8')
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
    importer = sub.add_parser('import-issue', help='Import a translation ZIP attached to an issue (body from $ISSUE_BODY)')
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
        site(args.output.resolve(), args.browser)
    else:
        import_issue(os.environ.get('ISSUE_BODY', ''), args.issue, args.output.resolve(), args.browser)


if __name__ == '__main__':
    main()
