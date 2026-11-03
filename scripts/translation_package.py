#!/usr/bin/env python3
"""Export a translator handoff and validate returned Markdown and label files.

The export runs the real manual build with a recording localizer, so the package holds
exactly the strings and Markdown the build uses, each with the pages where it appears."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from string import Template
import shutil
import subprocess
import tempfile
import zipfile

from manual_localization import RecordingLocalizer
from manual_paths import MODEL_CATEGORIES, ROOT, content_directory

# Packages exported before manifest schema 2 record no protected terms; these were the rules.
LEGACY_PROTECTED = {
    'hardware_letters': 'ABCDEFGH',
    'terms': ['S630', 'S640', 'ATX', 'SFX', 'SFX-L', 'EATX', 'PCIe', 'USB', 'USB-A', 'USB-C', 'p-5-100013b'],
    'patterns': [r'M\d+(?:\.\d+)?'],
}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def write_json(path, value):
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected_terms(models):
    """Protected text for a package: glossary terms, all model SKUs and the models' hardware letters."""
    glossary = read_json(ROOT / 'glossary/protected-terms.json')
    letters = {item['letter'] for model in models
               for item in read_json(content_directory(model) / 'hardware.json')['items']}
    assert all(re.fullmatch('[A-Z]', letter) for letter in letters), letters
    return {'hardware_letters': ''.join(sorted(letters)),
            'terms': sorted(set(MODEL_CATEGORIES) | set(glossary['terms']) | set(glossary['part_numbers'])),
            'patterns': glossary['patterns']}


def protected_spec(manifest):
    return manifest.get('protected') or LEGACY_PROTECTED


def term_pattern(spec):
    # Longest first, so SFX-L is preferred to SFX; the editor builds the same expression.
    terms = sorted(set(spec['terms']), key=lambda term: (-len(term), term))
    return r'\b(?:' + '|'.join([re.escape(term) for term in terms] + spec['patterns']) + r')\b'


def name_list(items):
    items = list(items)
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]


def manuals_label(models, version):
    """'S630 and S640 v1.0', or the version text itself when it already names each model."""
    return version if all(model in version for model in models) else f'{name_list(models)} {version}'


def handoff_readme(models, version, markdown_files, protected, family):
    """docs/translation-handoff.md with this package's models, folders and family notes."""
    template = re.sub(r'<!--.*?-->\n*', '', (ROOT / 'docs/translation-handoff.md').read_text(encoding='utf-8'), flags=re.S)
    notes = ROOT / 'docs/translation-notes' / f'{family}.md'
    folders = []
    for path in markdown_files:
        parts = Path(path).relative_to('content/en').parts
        folder = 'translation/content/' + ('shared' if parts[0] == 'shared' else '/'.join(parts[:2])) + '/'
        if folder not in folders:
            folders.append(folder)
    letters = protected['hardware_letters']
    contiguous = letters == ''.join(chr(ord(letters[0]) + k) for k in range(len(letters)))
    glossary = read_json(ROOT / 'glossary/protected-terms.json')
    return Template(template).substitute(
        manuals=manuals_label(models, version), version=version,
        content_folders=name_list(f'`{folder}`' for folder in sorted(folders)),
        hardware_letters=f'{letters[0]}–{letters[-1]}' if contiguous and len(letters) > 2 else ', '.join(letters),
        terms=', '.join(glossary['terms']) + ', screw sizes such as M3 and 6-32',
        family_notes=notes.read_text(encoding='utf-8').strip() + '\n' if notes.is_file() else '')


def export(destination, models, include_drafts=False):
    import manual_build
    if destination.exists():
        raise ValueError(f'Output already exists: {destination}; choose a new folder.')
    manuals = {model: manual_build.manual(model) for model in models}
    drafts = [model for model, manual in manuals.items() if not manual.get('release_ready')]
    if drafts and not include_drafts:
        raise ValueError(f'Not approved releases: {", ".join(drafts)} (use --include-drafts for a trial package)')
    families = {manual_build.family(model) for model in models}
    if len(families) != 1:
        raise ValueError('Export models from one manual family at a time: ' + ', '.join(sorted(families)))
    revisions = {model: manual['revision'] for model, manual in manuals.items()}
    version = revisions[models[0]] if len(set(revisions.values())) == 1 else \
        name_list(f'{model} {revision}' for model, revision in revisions.items())
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--', 'content', 'products', 'templates'],
                                    cwd=ROOT, text=True).strip()
    if dirty:
        print('Warning: uncommitted English content/template changes; the recorded source commit will not match:\n' + dirty)

    recorder = RecordingLocalizer()
    for model in models:
        recorder.model = model
        manual_build.build(model, None, localizer=recorder, render_only=True)
    catalog = {'s_' + hashlib.sha256(text.encode()).hexdigest()[:16]: {'source': text, 'translation': '', 'contexts': contexts}
               for text, contexts in recorder.strings.items()}
    assert len(catalog) == len(recorder.strings), 'String ID collision'
    markdown_files = sorted(recorder.markdown_files)

    destination.mkdir(parents=True)
    for path in markdown_files:
        relative = Path(path).relative_to('content/en')
        for prefix in ('source/content/en', 'translation/content'):
            write_text(destination / prefix / relative, recorder.markdown_files[path])
    for model in models:
        if model in drafts:
            print(f'Note: {model} is a draft; the package has no reference PDF for it')
            continue
        revision = revisions[model]
        pdf = ROOT / 'releases/en' / MODEL_CATEGORIES[model] / model / revision / f'{model}-en-{revision}.pdf'
        target = destination / 'reference' / pdf.relative_to(ROOT / 'releases')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, target)
    protected = protected_terms(models)
    write_json(destination / 'source/strings.json', catalog)
    write_json(destination / 'translation/strings.json', catalog)
    write_json(destination / 'translation/job.json', {
        'source_language': 'en', 'target_language': '', 'target_language_name': '',
        'translator': '', 'reviewer': '', 'notes': '',
    })
    write_json(destination / 'page-map.json', recorder.pages)
    write_text(destination / 'README.md', handoff_readme(models, version, markdown_files, protected, families.pop()))
    shutil.copy2(ROOT / 'glossary/README.md', destination / 'terminology.md')
    baseline = {path.relative_to(destination).as_posix(): digest(path)
                for sub in ('source', 'reference') for path in sorted((destination / sub).rglob('*')) if path.is_file()}
    write_json(destination / 'manifest.json', {
        'schema_version': 2, 'models': list(models), 'source_language': 'en', 'source_version': version,
        'source_versions': revisions, 'drafts': drafts,
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'protected': protected,
        'repository_source_sha256': {path: hashlib.sha256(recorder.markdown_files[path].encode()).hexdigest()
                                     for path in markdown_files},
        'baseline_sha256': baseline,
        'markdown_files': markdown_files,
    })
    print(f'Exported {len(markdown_files)} Markdown files and {len(catalog)} unique strings '
          f'for {manuals_label(models, version)} to {destination}')


def protected(text, spec=LEGACY_PROTECTED):
    """Tokens that must survive translation; prose remains freely editable."""
    without_jinja = re.sub(r'{{.*?}}|{%.*?%}', '', text, flags=re.S)
    letters = '[' + spec['hardware_letters'] + ']'
    return {
        'Jinja expressions/conditions': re.findall(r'{{.*?}}|{%.*?%}', text, re.S),
        'HTML tags/attributes': re.findall(r'</?[A-Za-z][^>]*>', without_jinja),
        'URLs/email addresses': Counter(re.findall(r'https?://[^\s<>]+|[\w.+-]+@[\w.-]+\.[A-Za-z]+', without_jinja)),
        'hardware references': Counter(re.findall(rf'\*\*({letters})\*\*|<strong>({letters})</strong>', without_jinja)),
        'headings': re.findall(r'^\s*(#{1,6})\s', text, re.M),
        'list structure': re.findall(r'^\s*(\d+\.|[-*])\s', text, re.M),
        'table structure': [line.count('|') for line in text.splitlines() if line.lstrip().startswith('|')],
        'Markdown hard line breaks': len(re.findall(r' {2,}\n', text)),
        'numeric values': Counter(re.findall(r'(?<![\w])\d+(?:[.,]\d+)*', without_jinja)),
        'technical identifiers': Counter(re.findall(term_pattern(spec), without_jinja)),
    }


def default_baseline(package):
    """The repository copy of a package with the same name, used for omitted read-only files."""
    candidate = ROOT / 'translation-packages' / package.name
    return candidate if candidate.is_dir() and candidate.resolve() != package.resolve() else None


def validate(package, complete=False, baseline=None):
    """Validate a returned package. Read-only files it omits (the browser editor leaves out
    the reference PDFs) are taken from `baseline`, by default the repository's copy."""
    baseline = baseline or default_baseline(package)

    def locate(name):
        path = package / name
        return path if path.exists() or not baseline else baseline / name

    manifest = read_json(locate('manifest.json'))
    spec = protected_spec(manifest)
    errors, warnings = [], []
    for name, checksum in manifest['baseline_sha256'].items():
        path = locate(name)
        if not path.is_file() or digest(path) != checksum:
            errors.append('Changed/missing read-only baseline: ' + name)
    for name in manifest['markdown_files']:
        relative = Path(name).relative_to('content/en')
        source = locate('source/content/en/' + relative.as_posix())
        target = package / 'translation/content' / relative
        if not source.is_file() or not target.is_file():
            errors.append('Missing Markdown: ' + str(relative))
            continue
        original = source.read_text(encoding='utf-8')
        translated = target.read_text(encoding='utf-8')
        if not translated.strip():
            errors.append('Empty Markdown: ' + str(relative))
        if original == translated:
            warnings.append('Unchanged Markdown (review): ' + str(relative))
        old, new = protected(original, spec), protected(translated, spec)
        for token in old:
            if old[token] != new[token]:
                errors.append(f'{relative}: changed {token}')
    baseline = read_json(locate('source/strings.json'))
    translated = read_json(package / 'translation/strings.json')
    if baseline.keys() != translated.keys():
        errors.append('String IDs added or removed')
    for key, entry in baseline.items():
        result = translated.get(key, {})
        if set(result) != set(entry) or result.get('source') != entry['source'] or result.get('contexts') != entry['contexts']:
            errors.append('Changed source/context/fields: ' + key)
        value = result.get('translation')
        if not isinstance(value, str):
            errors.append('Non-text translation: ' + key)
        elif not value.strip():
            (errors if complete else warnings).append('Untranslated string: ' + key)
        else:
            old, new = protected(entry['source'], spec), protected(value, spec)
            for token in old:
                if old[token] != new[token]:
                    errors.append(f'{key}: changed {token}')
    job = read_json(package / 'translation/job.json')
    if complete and (not job.get('target_language') or not job.get('target_language_name')):
        errors.append('Set target_language and target_language_name in translation/job.json')
    expected = {str(Path(name).relative_to('content/en')) for name in manifest['markdown_files']}
    actual = {str(path.relative_to(package / 'translation/content'))
              for path in (package / 'translation/content').rglob('*') if path.is_file()}
    if expected != actual:
        errors.append('Translation Markdown files added or removed')
    for message in errors:
        print('ERROR:', message)
    print(f'{len(errors)} errors; {len(warnings)} items requiring translation/review.')
    if errors:
        raise ValueError('Package validation failed')
    print('PASS: Package structure and protected tokens are intact. Human language and PDF layout review still required.')


def extract_package(archive, destination):
    """Extract a returned ZIP and return its single top-level package folder."""
    with zipfile.ZipFile(archive) as source:
        for name in source.namelist():
            if name.startswith(('/', '\\')) or '..' in Path(name).parts:
                raise ValueError('Unsafe path in ZIP: ' + name)
        source.extractall(destination)
    folders = [path for path in destination.iterdir() if path.is_dir()]
    if len(folders) != 1 or any(path.is_file() for path in destination.iterdir()):
        raise ValueError('ZIP must contain exactly one package folder')
    return folders[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    export_parser = sub.add_parser('export', help='Export a handoff for released manuals that share a revision')
    export_parser.add_argument('directory', type=Path)
    export_parser.add_argument('--models', nargs='+', required=True, choices=sorted(MODEL_CATEGORIES),
                               help='Manuals translated together; shared text appears once')
    export_parser.add_argument('--include-drafts', action='store_true',
                               help='Allow unreleased manuals (trial packages; their English may still change)')
    check = sub.add_parser('validate', help='Validate a returned package folder or ZIP')
    check.add_argument('directory', type=Path)
    check.add_argument('--complete', action='store_true')
    check.add_argument('--baseline', type=Path,
                       help='Original package supplying omitted read-only files '
                            '(default: translation-packages/<same name>)')
    archive = sub.add_parser('zip')
    archive.add_argument('directory', type=Path)
    archive.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.command == 'export':
        export(args.directory.resolve(), args.models, args.include_drafts)
    elif args.command == 'validate':
        baseline = args.baseline.resolve() if args.baseline else None
        if args.directory.suffix.lower() == '.zip':
            with tempfile.TemporaryDirectory() as temporary:
                validate(extract_package(args.directory, Path(temporary)), args.complete, baseline)
        else:
            validate(args.directory.resolve(), args.complete, baseline)
    else:
        validate(args.directory.resolve())
        if args.output.resolve().is_relative_to(args.directory.resolve()):
            raise ValueError('ZIP output must be outside the package folder.')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(args.directory.rglob('*')):
                if path.is_file():
                    archive.write(path, Path(args.directory.name) / path.relative_to(args.directory))
        print('Created', args.output)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
