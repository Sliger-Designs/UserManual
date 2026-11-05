# Sliger user manuals

Source for Sliger Designs chassis user manuals: Markdown text, product data, selected
illustrations, the templates and scripts that build them into print-ready PDFs, and the
tools used to translate them.

| Model | Form factor | Status | English PDF |
|---|---|---|---|
| S630 | Desktop (SFF) | Released v1.0 (2026-11-02) | [PDF](releases/en/desktop/S630/v1.0/S630-en-v1.0.pdf) |
| S640 | Desktop (SFF) | Released v1.0 (2026-11-02) | [PDF](releases/en/desktop/S640/v1.0/S640-en-v1.0.pdf) |
| CX3150a | 3U rackmount | Review draft (Prototype 0.3) | built by CI and on the site |
| CX3150i | 3U rackmount, one 5.25" bay | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3150x | 3U rackmount, internal drive bracket | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3151a | 3U rackmount, riser GPU | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3151i | 3U rackmount, one 5.25" bay, riser GPU | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3151x | 3U rackmount, internal drive bracket, riser GPU | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3152a | 3U rackmount, ATX power supply | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3152i | 3U rackmount, one 5.25" bay, ATX power supply | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3170a | 3U rackmount, 17-inch | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3171a | 3U rackmount, 17-inch, riser GPU | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3172a | 3U rackmount, 17-inch, ATX power supply | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3170a XL | 3U rackmount, 17-inch, XL tray, drive cage | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3170i XL | 3U rackmount, 17-inch, XL tray, one 5.25" bay | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3171a XL | 3U rackmount, 17-inch, XL tray, riser GPU, drive cage | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3171i XL | 3U rackmount, 17-inch, XL tray, one 5.25" bay, riser GPU | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3172a XL | 3U rackmount, 17-inch, XL tray, ATX power supply | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3172i XL | 3U rackmount, 17-inch, XL tray, one 5.25" bay, ATX power supply | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3701 | 3U NAS, 15-inch, Mini-ITX, 10 × 3.5" hot-swap | Review draft (Prototype 0.1) | built by CI and on the site |
| CX3702 | 3U NAS, 18-inch, MicroATX, 10 × 3.5" hot-swap | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4150a | 4U rackmount | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4150e | 4U rackmount, two 5.25" bays | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4150i | 4U rackmount, one 5.25" bay | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4170a | 4U rackmount | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4170e | 4U rackmount, two 5.25" bays | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4170i | 4U rackmount, one 5.25" bay | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4200a | 4U rackmount | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4200e | 4U rackmount, two 5.25" bays | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4200f | 4U rackmount, three 5.25" bays | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4200i | 4U rackmount, one 5.25" bay | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4712 | 4U NAS, 10 hot-swap + 2 × 5.25" bays | Review draft (Prototype 0.1) | built by CI and on the site |
| CX4713 | 4U NAS, 10 hot-swap + 2 × 5.25" bays | Review draft (Prototype 0.1) | built by CI and on the site |

## Repository layout

- `content/en/<category>/<model>/`: each manual's Markdown and `manual.json`, which sets
  page order, titles, layouts and the images and captions on each page. Text used by several
  manuals is in `content/en/shared/`. Categories are lowercase (`desktop`, `2u`, `3u`,
  `4u`); model casing is preserved (`S630`, `CX3150a`).
- `products/`: product facts (dimensions, clearances, supported parts) with their
  provenance. `products/overrides.json` records explicit decisions, which take
  precedence; `products/shared/` holds shared hardware kits and compatibility rules.
- `illustrations/published/`: the image copies used in the manuals, with checksums and
  transformation records. Full-resolution originals are not in Git.
- `templates/`: HTML template, styles, fonts and logo; `templates/translation-editor/`
  is the browser translation editor.
- `scripts/`: builds, checks, translation tools and CI tasks (below).
- `releases/<language>/<category>/<model>/<revision>/`: approved release PDFs.
- `translation-packages/` and `translations/`: translator handoffs and per-language
  translation memories.
- `sources/`: archived public references (the original CX3150a manual and website
  specifications) and `sources/decisions/`, the decisions behind approved specifications.
- `glossary/`: approved terminology and the protected terms translators keep unchanged.

Some provenance fields in `products/` and `content/` refer to working files (catalog
exports, design snapshots) that are kept in Sliger's private archive.

## Build a manual

Requires Python 3.12+.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python scripts/build_manual.py --model S630
```

Every model builds the same way (`--model S640`, `CX3150a`, `CX3150i`, `CX3150x`, `CX3151a`, `CX3151i`, `CX3151x`, `CX3152a`, `CX3152i`, `CX3170a`, `CX3171a`, `CX3172a`, `CX3170aXL`, `CX3170iXL`, `CX3171aXL`, `CX3171iXL`, `CX3172aXL`, `CX3172iXL`, `CX3701`, `CX3702`, `CX4150a`, `CX4150e`, `CX4150i`, `CX4170a`, `CX4170e`, `CX4170i`, `CX4200a`, `CX4200e`, `CX4200f`, `CX4200i`, `CX4712`, `CX4713`). A build writes
standalone HTML, a landscape Letter PDF, a page overview and a validation report under
`_build/`, and fails if text overflows a page, a link breaks, an image is missing, or
approved values or wording differ. Released SFF manuals build into
`_build/releases/chassis/<model>/<revision>/`; drafts into `_build/unpublished/chassis/<model>/`.
Builds never replace files in `releases/`; archiving an approved PDF is a separate,
reviewed commit (see [releases/README.md](releases/README.md)).

Both manual families (`build_sff_manual.py`, `build_rackmount_manual.py`) share one
interface through `scripts/manual_build.py`, which all tools use.

## Edit text

Edit the Markdown under `content/en/`. Shared files change every manual that uses them.
Open a pull request: the *Manual checks* workflow rebuilds the manuals the change affects
and attaches their PDFs (see [docs/ci-and-publishing.md](docs/ci-and-publishing.md)).
Small text edits can be made entirely on GitHub.

New pages, new images or a new manual need a local checkout: originals are recorded with
`scripts/inventory_originals.py`, publication copies are prepared with
`scripts/prepare_assets.py`, and callout positions are checked visually. Each rackmount
`manual.json` lists the approved values its PDF must show in `text_checks`.

## Translations

Translators use a single-file browser editor that shows each page as sentence-sized items
beside a live preview, protects placeholders, hardware letters, numbers and model names,
and exports a ZIP. Returned translations are imported into `translations/<lang>/memory.json`,
so text shared between manuals is translated once and only changed text needs work later.

```bash
python3 scripts/translation_package.py export /path/to/package --models S630 S640
python3 scripts/translation_editor.py translation-packages/S630-S640-v1.0-en
python3 scripts/translation_memory.py import /path/to/returned.zip
python3 scripts/build_manual.py --model S630 --language de
```

See [translation-packages/README.md](translation-packages/README.md) and
[translations/README.md](translations/README.md). Translators can also return ZIPs through
the *Return a translation* issue form; a maintainer approves the automatic import.

## Checks and publishing

Pull requests run the builds and checks they affect; pushes to `main` publish translation
editors and preview PDFs to GitHub Pages. See
[docs/ci-and-publishing.md](docs/ci-and-publishing.md) for the workflows and one-time setup.

## License

The code (`scripts/`, the templates and stylesheets in `templates/`, `.github/`) is
available under the [MIT License](LICENSE). The manual content (text, product data,
illustrations, PDFs and translations) and the Sliger name and logo are © Sliger Designs
LLC, all rights reserved; see [NOTICE.md](NOTICE.md). Titillium Web is used under the
[SIL Open Font License](templates/fonts/OFL.txt).
