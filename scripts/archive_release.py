#!/usr/bin/env python3
"""Archive approved English manuals into releases/ after building them.

For each model (release_ready, with a release_date), copies the release build
_build/releases/chassis/<model>/<revision>/<model>-en-<revision>.pdf to
releases/en/<category>/<model>/<revision>/ and writes a release record beside it with the
build's content fingerprint. Builds then fail if that revision's content changes, and the
site shows the main-branch preview only when it differs from the latest release.
Archived versions are never replaced. --record-only writes the record for a PDF that is
already archived (the current build must be the released content)."""
import argparse
from datetime import date
import json
import shutil
import sys

import manual_build
from manual_assets import release_record_path
from manual_paths import MODEL_CATEGORIES, ROOT


def archive(model, record_only=False, note=None):
    manual = manual_build.manual(model)
    revision = manual['revision']
    if not manual.get('release_ready') or not manual.get('release_date'):
        raise SystemExit(f'{model}: set "release_ready": true and "release_date" before archiving')
    built = manual_build.build(model, None)
    report = json.loads(built['report'].read_text(encoding='utf-8'))
    record_path = release_record_path(model, MODEL_CATEGORIES[model], revision)
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
    record = {'model': model, 'language': 'en', 'revision': revision, 'release_date': manual['release_date'],
              'pdf': target.name, 'content_fingerprint': report['content_fingerprint'],
              'recorded': date.today().isoformat()}
    if note:
        record['note'] = note
    record_path.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'{model} {revision}: {"recorded" if record_only else "archived"} in {record_path.parent.relative_to(ROOT)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--models', nargs='+', required=True, choices=sorted(MODEL_CATEGORIES))
    parser.add_argument('--record-only', action='store_true', help='Only write the record for an already archived PDF')
    parser.add_argument('--note', help='Note stored in the record')
    args = parser.parse_args()
    for model in args.models:
        archive(model, args.record_only, args.note)


if __name__ == '__main__':
    sys.exit(main())
