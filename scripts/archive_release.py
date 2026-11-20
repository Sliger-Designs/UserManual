#!/usr/bin/env python3
"""Archive approved manuals into releases/ after building them.

For each model (release_ready, with a release_date), copies the release build
_build/releases/chassis/<model>/<revision>/<model>-en-<revision>.pdf to
releases/en/<category>/<model>/<revision>/ and writes a release record beside it with the
build's content fingerprint. Builds then fail if that revision's content changes, and the
site shows the main-branch preview only when it differs from the latest release.
Archived versions are never replaced. --record-only writes the record for a PDF that is
already archived (the current build must be the released content).

--language <code> archives an approved translation instead: the manual is built from
translations/<code>/memory.json (it must be complete) and archived as
releases/<code>/<category>/<model>/<revision>/<model>-<code>-<revision>.pdf. The English
revision it translates must already be released; the release date is today unless
--release-date is given."""
import argparse
from datetime import date
import json
import shutil
import sys

import manual_build
from manual_assets import release_record_path
from manual_paths import MODEL_CATEGORIES, ROOT


def archive(model, record_only=False, note=None, language='en', release_date=None):
    manual = manual_build.manual(model)
    revision = manual['revision']
    if not manual.get('release_ready') or not manual.get('release_date'):
        raise SystemExit(f'{model}: set "release_ready": true and "release_date" before archiving')
    if language == 'en':
        built = manual_build.build(model, None)
        release_date = manual['release_date']
    else:
        if not release_record_path(model, MODEL_CATEGORIES[model], revision).is_file():
            raise SystemExit(f'{model}: English {revision} is not released; a translation releases a released revision')
        from translation_memory import MemoryLocalizer
        dry = MemoryLocalizer(language)
        manual_build.build(model, None, localizer=dry, render_only=True)
        if dry.report():
            raise SystemExit(f'{model}: translations/{language} is incomplete for this manual')
        built = manual_build.build(model, None, localizer=MemoryLocalizer(language))
        release_date = release_date or date.today().isoformat()
    report = json.loads(built['report'].read_text(encoding='utf-8'))
    record_path = release_record_path(model, MODEL_CATEGORIES[model], revision, language)
    target = record_path.with_suffix('.pdf')
    if record_path.exists():
        raise SystemExit(f'{model} {revision} already has a release record: {record_path.relative_to(ROOT)}')
    if record_only:
        if not target.is_file():
            raise SystemExit(f'{model}: no archived PDF at {target.relative_to(ROOT)}')
    else:
        if target.exists():
            raise SystemExit(f'{model} {revision} is already archived; release a new revision instead')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built['pdf'], target)
    record = {'model': model, 'language': language, 'revision': revision, 'release_date': release_date,
              'pdf': target.name, 'content_fingerprint': report['content_fingerprint'],
              'recorded': date.today().isoformat()}
    if note:
        record['note'] = note
    record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'{model} {revision}: {"recorded" if record_only else "archived"} in {record_path.parent.relative_to(ROOT)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--models', nargs='+', required=True, choices=sorted(MODEL_CATEGORIES))
    parser.add_argument('--record-only', action='store_true', help='Only write the record for an already archived PDF')
    parser.add_argument('--note', help='Note stored in the record')
    parser.add_argument('--language', default='en', help='Archive an approved translation (e.g. de) instead of English')
    parser.add_argument('--release-date', help='Translation release date (default: today)')
    args = parser.parse_args()
    for model in args.models:
        archive(model, args.record_only, args.note, args.language, args.release_date)


if __name__ == '__main__':
    sys.exit(main())
