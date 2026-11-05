# Illustrations

Artwork still needed for the manuals is tracked in [ARTWORK-REQUESTS.md](ARTWORK-REQUESTS.md).

Full-resolution originals (CAD renders and photographs) are kept in Sliger's internal
image library and are not in Git. A maintainer stages the chassis being worked on
locally, in the ignored `<category>/<model>/` folders (`desktop/S630/`, `3u/CX3150a/`,
…), and prepares publication copies from them with `scripts/prepare_assets.py`.

## What is versioned

- `published/<model>/` and `published/common/`: the selected, appropriately sized copies
  the manuals use. Each folder's `manifest.json` records every file's checksum, its source
  file's checksum, dimensions, and the exact transformation (crop, resize, background
  cleanup). Builds use only these files and check their hashes.
- `<model>.inventory.json`, `common.inventory.json`, `reference.inventory.json`: every
  supplied original with dimensions, checksum and selection status, so a publication copy
  can always be traced to its original.
- `common/`: small shared originals stored once (hardware fasteners, front I/O connector
  drawings, regulatory icons, shared storage and PSU bracket views).
- `reference/CX3150a/`: diagrams recovered from the original CX3150a manual
  (`scripts/extract_reference_assets.py`).
- `published/covers/`: website product photographs used on the covers
  (`scripts/fetch_cover_photos.py`).

## Working rules

- Never modify originals. Record crop, resize and cleanup choices in the manifest, and
  keep source hashes so a changed original is detected.
- Use one published asset wherever a procedure is genuinely shared.
- Keep text out of images where possible: numbered callouts and hardware letters are
  drawn as vector overlays from `*-callouts.json` / `*-framing.json` annotations in each
  model's `content/` folder, bound to the source image's hash and coordinates, so they can
  be translated and stay aligned. Re-check positions whenever a source image changes.
- Background cleanup (flat gray render backgrounds to white) changes only pixels within
  the recorded tolerance; settings and counts are recorded per asset.
- Folder categories are lowercase (`desktop`, `2u`, `3u`, `4u`) and match
  `content/en/<category>/<model>/`; model casing and original filenames are preserved.

Decisions about specific artwork (for example a different but approved standoff
render for hardware C) are recorded in `sources/decisions/`.
