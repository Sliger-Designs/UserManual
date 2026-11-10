# Released manuals

These PDFs are the approved release artifacts, committed so they are available
with a clone or pull. Temporary builds, HTML and previews remain in the ignored
`_build/` directory.

Use `releases/<language>/<form-factor>/<model>/<version>/`, matching the content
hierarchy. Language codes use lowercase (`en`); form-factor categories use the
existing lowercase names (`desktop`, `2u`, `3u`, `4u`). Keep model/SKU casing
unchanged. Add language folders when translations are approved.

| Language | Form factor | Model | Version | Release date | Manual |
|---|---|---|---|---|---|
| English (`en`) | Desktop | S630 | v1.0 | 2026-11-02 | [PDF](en/desktop/S630/v1.0/S630-en-v1.0.pdf) |
| English (`en`) | Desktop | S640 | v1.0 | 2026-11-02 | [PDF](en/desktop/S640/v1.0/S640-en-v1.0.pdf) |
| English (`en`) | 4U | CX4150a | v1.0 | 2026-11-09 | [PDF](en/4u/CX4150a/v1.0/CX4150a-en-v1.0.pdf) |
| English (`en`) | 4U | CX4150e | v1.0 | 2026-11-09 | [PDF](en/4u/CX4150e/v1.0/CX4150e-en-v1.0.pdf) |
| English (`en`) | 4U | CX4150i | v1.0 | 2026-11-09 | [PDF](en/4u/CX4150i/v1.0/CX4150i-en-v1.0.pdf) |
| English (`en`) | 4U | CX4170a | v1.0 | 2026-11-09 | [PDF](en/4u/CX4170a/v1.0/CX4170a-en-v1.0.pdf) |
| English (`en`) | 4U | CX4170e | v1.0 | 2026-11-09 | [PDF](en/4u/CX4170e/v1.0/CX4170e-en-v1.0.pdf) |
| English (`en`) | 4U | CX4170i | v1.0 | 2026-11-09 | [PDF](en/4u/CX4170i/v1.0/CX4170i-en-v1.0.pdf) |
| English (`en`) | 4U | CX4200a | v1.0 | 2026-11-09 | [PDF](en/4u/CX4200a/v1.0/CX4200a-en-v1.0.pdf) |
| English (`en`) | 4U | CX4200e | v1.0 | 2026-11-09 | [PDF](en/4u/CX4200e/v1.0/CX4200e-en-v1.0.pdf) |
| English (`en`) | 4U | CX4200f | v1.0 | 2026-11-09 | [PDF](en/4u/CX4200f/v1.0/CX4200f-en-v1.0.pdf) |
| English (`en`) | 4U | CX4200i | v1.0 | 2026-11-09 | [PDF](en/4u/CX4200i/v1.0/CX4200i-en-v1.0.pdf) |
| English (`en`) | 3U | CX3150a | v1.1 | 2026-11-10 | [PDF](en/3u/CX3150a/v1.1/CX3150a-en-v1.1.pdf) |
| English (`en`) | 3U | CX3150i | v1.0 | 2026-11-10 | [PDF](en/3u/CX3150i/v1.0/CX3150i-en-v1.0.pdf) |
| English (`en`) | 3U | CX3150x | v1.0 | 2026-11-10 | [PDF](en/3u/CX3150x/v1.0/CX3150x-en-v1.0.pdf) |
| English (`en`) | 3U | CX3151a | v1.0 | 2026-11-10 | [PDF](en/3u/CX3151a/v1.0/CX3151a-en-v1.0.pdf) |
| English (`en`) | 3U | CX3151i | v1.0 | 2026-11-10 | [PDF](en/3u/CX3151i/v1.0/CX3151i-en-v1.0.pdf) |
| English (`en`) | 3U | CX3151x | v1.0 | 2026-11-10 | [PDF](en/3u/CX3151x/v1.0/CX3151x-en-v1.0.pdf) |

Each version folder holds the PDF and a release record (`<model>-en-<version>.json`) with
the release date and a content fingerprint of the build: a hash of its visible text and
images (styling excluded).

## Releasing a manual

1. Set `revision` (e.g. `v1.0`), `status`, `release_ready: true` and `release_date` in the
   manual's `manual.json`, and add the version to its revision history.
2. Archive it: `python scripts/archive_release.py --models CX4150a` builds the manual, copies
   `_build/releases/chassis/<model>/<version>/<model>-en-<version>.pdf` here and writes the
   record. It never replaces an archived version.
3. Add the row to the table above and to the repository README, and commit.

## Changing a released manual

A released version's content is locked: a build fails if its content no longer matches the
release record. To change the manual, draft the next version: set `revision` to `v1.1` and
`release_ready` to `false`. While drafting, the site lists the main-branch build as
"v1.1 draft: unreleased changes since v1.0" next to the released PDF (which it otherwise
hides, since it would be identical). Release the new version with the steps above.
