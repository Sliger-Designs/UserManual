#!/usr/bin/env python3
"""Per-language translation memories: the stored form of every translation.

`translations/<lang>/memory.json` maps English text (a label, or one Markdown segment as
split by translation_segments.py) to its translation. One memory serves every manual and
version: shared text is translated once, and after English changes only new segments need
work. Returned packages are imported into it; manuals are built from English plus memory.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import tempfile

from manual_localization import Localizer
from manual_paths import MODEL_CATEGORIES, ROOT, content_directory
from translation_package import extract_package, protected, protected_terms, read_json, validate, write_json
from translation_segments import assemble, needs_translation, segment_markdown, segments

MEMORY_ROOT = ROOT / 'translations'
EDITOR_MEMORY = 'translation/translation-memory.json'


def current_protected():
    """Protected text for memory checks: all models with hardware data."""
    return protected_terms([model for model in MODEL_CATEGORIES if (content_directory(model) / 'hardware.json').is_file()])


class Memory:
    def __init__(self, language, root=MEMORY_ROOT):
        self.language = language
        self.path = Path(root) / language / 'memory.json'
        data = read_json(self.path) if self.path.is_file() else {}
        self.language_name = data.get('language_name', '')
        self.entries = data.get('entries', {})

    def translation(self, english):
        entry = self.entries.get(english)
        return entry['translation'] if entry else None

    def save(self):
        write_json(self.path, {'schema': 1, 'language': self.language, 'language_name': self.language_name,
                               'entries': dict(sorted(self.entries.items()))})


class MemoryLocalizer(Localizer):
    """Translated text from a language memory. Missing or invalid entries fall back to English
    and are collected, so a dry run (render_only) lists every gap before a real build."""

    def __init__(self, language, root=MEMORY_ROOT):
        self.memory = Memory(language, root)
        if not self.memory.entries:
            raise ValueError(f'No translation memory at {self.memory.path}')
        self.language = language
        self.spec = current_protected()
        self.missing, self.problems = {}, {}

    def describe(self):
        return self.memory.path.relative_to(ROOT).as_posix() if self.memory.path.is_relative_to(ROOT) else str(self.memory.path)

    def lookup(self, english, where):
        value = self.memory.translation(english)
        if value is None:
            if needs_translation(english, self.spec):
                self.missing.setdefault(english, where)
            return english
        old, new = protected(english, self.spec), protected(value, self.spec)
        changed = [kind for kind in old if old[kind] != new[kind]]
        if changed:
            self.problems.setdefault(english, f'{where}: changed {", ".join(changed)}')
            return english
        return value

    def text(self, english, use=None, page=None):
        return self.lookup(english, f'{use or "label"}' + (f', page {page}' if page else ''))

    def markdown(self, path, english, layout=None, page=None):
        return assemble(segment_markdown(english), lambda part: self.lookup(part['text'], path))

    def report(self):
        return ([f'Missing ({where}): {english}' for english, where in self.missing.items()] +
                [f'Invalid ({english!r}) {problem}' for english, problem in self.problems.items()])


def package_translations(package):
    """English -> translation pairs in a package. Files win over the editor's memory file,
    which adds text deliberately left identical to English."""
    manifest = read_json(package / 'manifest.json') if (package / 'manifest.json').is_file() else None
    found, skipped = {}, []
    for entry in read_json(package / 'translation/strings.json').values():
        if isinstance(entry.get('translation'), str) and entry['translation'].strip():
            found[entry['source']] = entry['translation']
    names = manifest['markdown_files'] if manifest else []
    for name in names:
        relative = Path(name).relative_to('content/en')
        source, target = package / 'source/content/en' / relative, package / 'translation/content' / relative
        if not source.is_file() or not target.is_file():
            continue
        ours, theirs = segment_markdown(source.read_text(encoding='utf-8')), segment_markdown(target.read_text(encoding='utf-8'))
        shape = lambda segmented: [['text' if 'text' in part else part['fixed'] for part in parts] for parts in segmented['lines']]
        if shape(ours) != shape(theirs):
            skipped.append(relative.as_posix())
            continue
        for english, translated in zip(segments(ours), segments(theirs)):
            if translated['text'] != english['text']:
                found.setdefault(english['text'], translated['text'])
    editor_memory = package / EDITOR_MEMORY
    if editor_memory.is_file():
        for english, value in read_json(editor_memory).get('entries', {}).items():
            if isinstance(value, str) and value.strip():
                found.setdefault(english, value)
    return found, skipped


def import_package(path, root=MEMORY_ROOT):
    """Validate a returned package (folder or ZIP) and merge its translations into its language's memory."""
    path = Path(path).resolve()
    with tempfile.TemporaryDirectory() as temporary:
        package = extract_package(path, Path(temporary)) if path.suffix.lower() == '.zip' else path
        validate(package)
        job = read_json(package / 'translation/job.json')
        language = (job.get('target_language') or '').strip()
        if not re.fullmatch(r'[a-z]{2,3}(-[A-Za-z0-9]{2,8})*', language) or language == 'en':
            raise ValueError(f'Set target_language in translation/job.json to a language code such as "de" (found {language!r})')
        found, skipped = package_translations(package)
        models = read_json(package / 'manifest.json')['models']
        memory = Memory(language, root)
        if job.get('target_language_name'):
            memory.language_name = job['target_language_name']
        counts = {'added': 0, 'changed': 0, 'unchanged': 0}
        today = date.today().isoformat()
        for english, translation in found.items():
            current = memory.translation(english)
            if current == translation:
                counts['unchanged'] += 1
                continue
            counts['added' if current is None else 'changed'] += 1
            memory.entries[english] = {'translation': translation, 'package': package.name, 'imported': today,
                                       'translator': job.get('translator', ''), 'reviewer': job.get('reviewer', '')}
        memory.save()
        write_json(memory.path.parent / 'imports' / f'{package.name}.json',
                   {'package': package.name, 'file': path.name, 'imported': today, 'job': job,
                    **counts, 'markdown_not_imported': skipped})
    print(f'{language}: {counts["added"]} added, {counts["changed"]} changed, {counts["unchanged"]} unchanged '
          f'from {package.name} -> {memory.path.relative_to(ROOT) if memory.path.is_relative_to(ROOT) else memory.path}')
    for name in skipped:
        print(f'Not imported (Markdown structure differs from English; translate it in the editor): {name}')
    return {'memory': memory, 'language': language, 'package': package.name, 'models': models,
            'counts': counts, 'skipped': skipped, 'job': job}


def status(language, models, root=MEMORY_ROOT):
    """Which manuals can be built in a language now."""
    from manual_build import build
    ready = True
    for model in models:
        localizer = MemoryLocalizer(language, root)
        build(model, None, localizer=localizer, render_only=True)
        report = localizer.report()
        ready &= not report
        print(f'{model}: ' + ('ready to build' if not report else f'{len(localizer.missing)} missing, {len(localizer.problems)} invalid'))
        for line in report[:20]:
            print('   ', line)
        if len(report) > 20:
            print(f'    … and {len(report) - 20} more')
    return ready


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    importer = sub.add_parser('import', help='Validate a returned package folder or ZIP and merge it into translations/<lang>/')
    importer.add_argument('package', type=Path)
    check = sub.add_parser('status', help='Report which manuals a language memory can build')
    check.add_argument('language')
    check.add_argument('--models', nargs='+', required=True, choices=sorted(MODEL_CATEGORIES))
    args = parser.parse_args()
    if args.command == 'import':
        import_package(args.package)
    elif not status(args.language, args.models):
        raise SystemExit(1)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
