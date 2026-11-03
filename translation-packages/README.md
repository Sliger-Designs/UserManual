# Translation packages

[S630 and S640 v1.0 English handoff](S630-S640-v1.0-en/README.md) contains both
manuals' active Markdown, shared text, additional display/accessibility strings,
page maps, instructions and exact approved English PDFs. Shared material and
identical labels are included once.

The `source/` baseline and reference PDFs are snapshots. Translators edit only
`translation/` and return the whole package. Do not overwrite an existing handoff
when English content changes; export a new package and reconcile the differences.
`.gitattributes` keeps these files byte-exact on Windows checkouts, so their
checksums validate on every platform.

## Browser translation editor (recommended for translators)

Translators who do not work with text files or a command line can use a single
HTML page instead of the raw package. It shows each page of both manuals as
sentence-sized items beside a live preview of the real page, keeps headings,
lists, tables, placeholders and hardware letters locked, checks protected text
and page overflow as they type, and saves work in their browser, separately for each
language. It exports a translation ZIP for Sliger and prints either manual to PDF from
the browser. One editor serves every language: `index.html?lang=de` opens the German
translation (pre-filled from `translations/de/` when Sliger has one); without `?lang`
it lists the translations saved in that browser and offers a new one.

Build it (requires the same Python environment and Chromium as the manual build):

```bash
python3 scripts/translation_editor.py translation-packages/S630-S640-v1.0-en
python3 scripts/translation_editor_check.py _build/translation-editor/S630-S640-v1.0-en/index.html
```

The editor is `_build/translation-editor/S630-S640-v1.0-en/index.html` (about
22 MB, self-contained, works offline, nothing is uploaded). Send it directly or
host it as a static page. The check confirms that the editor's preview equals the
real build in English and after a pseudo-translation exported from the editor,
validated and rebuilt. Run it after changing templates or build scripts. The editor
refuses to build if the English content no longer matches the package snapshot.

The editor's ZIP omits the reference PDFs; validation reads them from the package
of the same name in this folder (or `--baseline`). Its
`translation/translation-memory.json` records every English → translation pair,
including text deliberately left unchanged; the editor reads it back when the ZIP
is reopened.

## Commands

Create a new handoff snapshot for released manuals of one family that are translated
together (shared text appears once). Any family works (SFF, rackmount); models may
have different revisions:

```bash
python3 scripts/translation_package.py export /path/to/new-package --models S630 S640
python3 scripts/translation_package.py export /path/to/trial --models CX3150a CX4170a --include-drafts
```

`--include-drafts` allows unreleased manuals for trial translations; their English may
still change and they have no reference PDFs.

The export runs the real manual build with a recording localizer, so the package
lists exactly the strings and Markdown the build uses, with each page where they
appear; nothing is maintained separately. The README is generated from
`docs/translation-handoff.md` plus `docs/translation-notes/<family>.md`.
Protected text (left unchanged by translators and checked by the validator and the
editor) is recorded in the manifest: terms and part numbers from
`glossary/protected-terms.json`, every model SKU, and the models' hardware letters.
The validator applies the rules a package was sent with (schema 1 packages such as
S630-S640-v1.0-en use the original list). The editor and builds from a translation
memory always apply the current rules, which include every older rule, so the editor
warns about anything a memory build would reject.

Create a sendable ZIP of the current package (output must not already exist):

```bash
python3 scripts/translation_package.py zip translation-packages/S630-S640-v1.0-en _build/translation-packages/S630-S640-v1.0-en.zip
```

Validate a returned package folder or ZIP:

```bash
python3 scripts/translation_package.py validate /path/to/returned.zip --complete
```

Store a returned package in its language's translation memory, the long-term home
of translations (see [translations/](../translations/README.md)), then build from it:

```bash
python3 scripts/translation_memory.py import /path/to/returned.zip
python3 scripts/build_manual.py --model S630 --language de
```

To review a returned package before importing it, build directly from the package
(it is validated first):

```bash
python3 scripts/build_manual.py --model S630 --translation /path/to/returned.zip
python3 scripts/build_manual.py --model S640 --translation /path/to/returned.zip
```

Output goes to `_build/unpublished/chassis/<model>/<language>/` with the usual
layout, overflow and link checks. Translated builds are never marked released.
Review every page for meaning and layout, approve the language, then archive its
PDFs under `releases/<language>/desktop/<model>/v1.0/` as a separate release step.
