# 4U motherboard-tray SSD mounting — November 4, 2026

Confirmed: every 4U chassis tray has the same SSD mounting at its rear: two
pairs of 2.5-inch mounting holes, taking either two SSDs up to 7 mm thick or one SSD up to
15 mm thick. Each drive is secured with two red-patched screws (hardware B). Neither pair can be used when the optional rear fan bracket is installed.

This extends the 2026-10-27 all-4U rule (`4u-rear-fan-blocks-tray-ssd` in
`products/shared/compatibility-rules.json`) from "the illustrated tray location" to both
mounting-hole pairs. It does not affect a separate drive cage.

Applied in `content/en/shared/rackmount/4u-ssd-installation.md`, used by every 4U manual's
SSD page, and `content/en/shared/rackmount/4u-rear-fan-ssd.md`.
