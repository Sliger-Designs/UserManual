#!/usr/bin/env python3
"""Build a standalone HTML manual, check its layout, then render its landscape PDF.

Any model can be built in English, from a returned translation (--translation),
or from a language's translation memory (--language)."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile

import manual_build
from manual_paths import MODEL_CATEGORIES


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--model', default='CX3150a', choices=sorted(MODEL_CATEGORIES))
    parser.add_argument('--browser', default=shutil.which('chromium') or shutil.which('google-chrome'),
                        help="Chromium executable (default: one on PATH, else Playwright's bundled Chromium)")
    parser.add_argument('--public-preview', action='store_true', help='Build customer-facing SFF PDFs without marking them released')
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--translation', type=Path, metavar='FILE',
                        help="Build review PDFs from a returned translation: the editor's .json file, an older ZIP or a package folder")
    source.add_argument('--language', metavar='LANG',
                        help='Build review PDFs from translations/LANG/memory.json')
    parser.add_argument('--allow-incomplete', action='store_true',
                        help='With --language: print missing text in English instead of stopping')
    args = parser.parse_args()
    model = args.model
    if args.public_preview and manual_build.family(model) != 'sff':
        parser.error('--public-preview currently supports SFF manuals (S630, S640)')
    options = {'public_preview': args.public_preview}
    if args.language:
        from translation_memory import MemoryLocalizer
        localizer = MemoryLocalizer(args.language)
        manual_build.build(model, None, localizer=localizer, render_only=True)  # Find every gap first.
        report = localizer.report()
        for line in report:
            print(line)
        if report and not args.allow_incomplete:
            raise SystemExit(f'{model}: {len(report)} texts missing or invalid in {localizer.describe()}; '
                             'import a translation or pass --allow-incomplete for a draft')
        manual_build.build(model, args.browser, localizer=MemoryLocalizer(args.language), **options)
    elif args.translation:
        from manual_localization import PackageLocalizer
        from translation_package import open_returned, validate
        with tempfile.TemporaryDirectory() as temporary:
            package = open_returned(args.translation, temporary)
            validate(package, complete=True)
            job = json.loads((package / 'translation/job.json').read_text(encoding='utf-8'))
            if job.get('translator') == 'self-test':
                # The CI editor check's accented pseudo-translation; built manuals from it look like
                # a corrupted translation, so they never go to the normal output folders.
                raise SystemExit('This is the editor self-test pseudo-translation, not a translation; it is not built as a manual')
            manual_build.build(model, args.browser, localizer=PackageLocalizer(package), **options)
    else:
        manual_build.build(model, args.browser, **options)


if __name__ == '__main__':
    main()
