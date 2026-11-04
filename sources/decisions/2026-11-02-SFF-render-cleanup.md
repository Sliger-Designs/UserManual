# S630 / S640 render backgrounds — November 2, 2026

Gray backgrounds were to be removed from existing renders because the
original CAD views were not saved. An image_gen trial removed the background but
changed colors/detail and reduced resolution; it was not selected for publication.
Non-AI pixel-based cleanup was explicitly authorized instead.

Eight source renders per model use the same flat background RGB (249, 251, 250).
Replace pixels within 4 levels per channel of that color with RGB white. Preserve
every other decoded source pixel, along with the original dimensions and framing.
This changes no geometry and does not require recreating the CAD views. The
original JPEG files and their inventory hashes remain unchanged.

`scripts/background_cleanup.py` implements the color-only operation.
`scripts/prepare_assets.py` applies the inventory's `background_cleanup` settings,
saves full-resolution cleaned PNGs under `_build/cleaned-renders/<model>/`, and
prepares lossless PNG publication copies. Each publication manifest records the
mask settings, pixel counts, full-resolution dimensions and output checksums.

The viewport crops and I/O assembly composition continue to use original-source
coordinates and hashes. Both the standard and flipped source renders are cleaned,
including the alternate assembly used as an SVG fragment.

The rejected AI trial and its exact prompt are retained locally in
`_build/unpublished/background-removal-trial/` for comparison; neither is used by
the manuals.
