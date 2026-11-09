# Translation packages

| Package | Manuals | Exported |
|---|---|---|
| [S630-S640-v1.0-en](S630-S640-v1.0-en/README.md) | S630, S640 v1.0 (superseded: support/warranty pages changed 2026-11-06) | 2026-11-02 |
| [S630-S640-v1.0-en-20261109](S630-S640-v1.0-en-20261109/README.md) | S630, S640 v1.0 | 2026-11-09 |
| [CX4150a-CX4150e-CX4150i-v1.0-en](CX4150a-CX4150e-CX4150i-v1.0-en/README.md) | CX4150a, CX4150e, CX4150i v1.0 (superseded by 4U-CX4150-CX4170-CX4200-v1.0-en; not sent) | 2026-11-09 |
| [4U-CX4150-CX4170-CX4200-v1.0-en](4U-CX4150-CX4170-CX4200-v1.0-en/README.md) | CX4150a, CX4150e, CX4150i, CX4170a, CX4170e, CX4170i, CX4200a, CX4200e, CX4200f, CX4200i v1.0 | 2026-11-09 |

A package is the English snapshot of released manuals that are translated together:
their Markdown and display/accessibility strings (shared text and identical labels once),
page maps, and hashes of the approved English PDFs in `releases/`. It is internal: nothing
here is sent to translators. Translators work only in the web editor built from a package,
and return one small translation file.

[`superseded.json`](superseded.json) maps replaced packages to their successors. Superseded
packages stay as records (and still validate), but only current packages get an editor on
the site. `.gitattributes` keeps package files byte-exact, so their checksums validate on
every platform.

## Export a package

Once the manuals are released:

```bash
python3 scripts/translation_package.py export translation-packages/<name> --models CX4150a CX4150e ...
python3 scripts/translation_package.py export /path/to/trial --models CX3150a CX4170a --include-drafts
```

Models must come from one family (SFF, rackmount) and may have different revisions.
`--include-drafts` allows unreleased manuals for trial translations; their English may still
change. The export runs the real manual build with a recording localizer, so the package
lists exactly the strings and Markdown the build uses, with each page where they appear;
nothing is maintained separately. Never overwrite a package: when English changes, export a
new one (for example with a date suffix), add the old name to `superseded.json`, and add a
row above.

Protected text (left unchanged by translators and checked by the validator and the editor)
is recorded in the manifest: terms and part numbers from `glossary/protected-terms.json`,
every model SKU, and the models' hardware letters. The validator applies the rules a
package was exported with (schema 1 packages such as S630-S640-v1.0-en use the original
list). The editor and builds from a translation memory always apply the current rules.

## The web editor

The Pages site builds one editor per current package (`ci.py site`). It shows each page of
the package's manuals as sentence-sized items beside a live preview of the real page, keeps
headings, lists, tables, placeholders and hardware letters locked, checks protected text
and page overflow as the translator types, and saves work in their browser, separately for
each language. One editor serves every language: `index.html?lang=de` opens the German
translation (pre-filled from `translations/de/` when Sliger has one). Images and fonts are
shared files in `editors/assets/`, named by content hash, and each manual's preview loads
only when one of its pages is opened. The translator instructions shown in the editor come
from `docs/translation-handoff.md`.

Build and check one locally (requires the same Python environment and Chromium as the
manual build):

```bash
python3 scripts/translation_editor.py translation-packages/S630-S640-v1.0-en-20261109
python3 scripts/translation_editor_check.py _build/translation-editor/S630-S640-v1.0-en-20261109/index.html
python3 -m http.server --directory _build/translation-editor   # then open http://localhost:8000/S630-S640-v1.0-en-20261109/
```

The editor needs a web server (opening the file directly does not load its fonts). The
check confirms that the editor's preview equals the real build in English and after a
pseudo-translation downloaded as a translation file, validated and rebuilt. Run it after
changing templates or build scripts. The editor refuses to build if the English content no
longer matches the package snapshot.

## Returned translations

The editor's **Download translation file** saves `<package>-<lang>-translation.json`: the
package name and English version it was made from, the translator's details and notes, and
every English → translation pair (including text deliberately left unchanged). Its
**Send to Sliger** explains the two ways back:

- **GitHub:** a pre-filled "Return a translation" issue with the file attached. Adding the
  label `import-translation` imports it, builds the manuals it completes and opens a pull
  request (see [docs/ci-and-publishing.md](../docs/ci-and-publishing.md)).
- **Email:** import the file yourself.

The file is expanded against its package here, then validated, built and imported like a
complete package:

```bash
python3 scripts/translation_package.py validate /path/to/<package>-de-translation.json --complete
python3 scripts/translation_memory.py import /path/to/<package>-de-translation.json
python3 scripts/build_manual.py --model S630 --language de
```

To review before importing, build directly from the file:

```bash
python3 scripts/build_manual.py --model S630 --translation /path/to/<package>-de-translation.json
```

Older editor ZIPs and package folders are still accepted by the same commands. The editor's
**Open file…** reads a translation file from any package: pairs are keyed by English text, so
a file from one package fills in every text another package shares with it.

Output goes to `_build/unpublished/chassis/<model>/<language>/` with the usual layout,
overflow and link checks. Translated builds are never marked released. Review every page
for meaning and layout, approve the language, then archive its PDFs under
`releases/<language>/<category>/<model>/<revision>/` as a separate release step.
