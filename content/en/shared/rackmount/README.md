# Verified shared pilot procedures

These Markdown files are currently used by CX3150a and CX4170a after comparing their existing manual text and image sequences. They are not automatically applicable to every rackmount chassis.

Each model selects its own illustrations and hardware callout placements. Product facts fill dimensional limits and rack-ear screw counts; shared SBAG-HWKIT definitions supply screw references. Model-specific drive/cooling and PSU procedures remain in each model folder.

Front connectors default to the supplied grayscale drawings. The front-panel location cutout remains model-specific until a common drawing is confirmed.

`4u-rear-fan-ssd.md` is an confirmed compatibility restriction for all 4U chassis. The build applies it automatically on the `ssd-installation` page when the product height is 4U, using `products/shared/compatibility-rules.json`. It does not apply to 3U manuals or rule out the separate drive cage.

`4u-ssd-installation.md` is the SSD page for every 4U chassis: all 4U trays share the same rear mounting (two 7 mm SSDs or one 15 mm SSD), confirmed 2026-11-04.

`3u-ssd-installation.md` is the SSD page for the 15-inch 3U chassis (CX3150a, CX3150i, CX3150x): their trays take two 7 mm SSDs or one 15 mm SSD, confirmed 2026-11-05. `two-fan-installation.md` replaces `fan-installation.md` on chassis with two front fans.

`bay-blank-drives.md` is the filler-blank page for every chassis with a 5.25-inch bay. The filler blank is one part shared across all of them (confirmed 2026-11-05), so every manual uses this page with the shared renders in `illustrations/common/4u-bay-blank/`.

`riser-rear-cover-removal.md`, `riser-gpu-brace.md`, `riser-gpu-installation.md` and `hardware-gpukit.md` cover the horizontal riser GPU of the CX3151a, CX3151i and CX3151x, with the CX3151-GPUKIT braces and screws (confirmed 2026-11-05).
