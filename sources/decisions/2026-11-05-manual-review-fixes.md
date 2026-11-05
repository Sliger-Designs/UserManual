# Manual review fixes — November 5, 2026

From a review pass over the rackmount manuals.

## All rackmount manuals

- **Units stay with their numbers.** The builder joins a number and its unit (mm, inches, kg, W,
  Gbps, slots) and the × between numbers with non-breaking spaces, so "270 mm" or
  "12 × 10.5 inches" never splits across lines.
- **Dimensions & compatibility:** the first column no longer wraps, so "Outer dimensions,
  D × W × H" stays on one line (rackmount only; the S630/S640 v1.0 layout is unchanged).
- **Larger step illustrations.** Procedure images are framed on their content (the render's
  empty margins are cropped at build time with `object-view-box`; the published files are
  unchanged). Filler-blank drive pages give the images more width (`wide-visuals`).

## 4U manuals

- **Exploded views** now use the S630/S640 style: a numbered part key beside the image and
  numbered badges on the parts (lid, faceplate and filter, 5.25-inch bay bracket or front fan
  bracket, front I/O, chassis wrap, motherboard tray), larger and at the top of the page.
- **Pages without renders are no longer omitted:** they show a grey placeholder where the image
  goes, for review (CX4712 exploded view and tray removal/reinstallation, CX4713 exploded view).
- **Rear fan bracket page** in every 4U manual, including the CX4712/CX4713: the same steps for
  every 4U tray (the CX415 tray is shallower than the CX417/CX420 trays). Placeholder until
  renders are supplied.
- CX4150i push-pull render replaced at the source; CX4150e 5.25-inch device page uses wider
  images (`medium-visuals`).

## Translations

The accented "pseudo-German" text seen in `_build/unpublished/chassis/S630|S640/de/` was the CI
editor self-test's pseudo-translation, built locally on 2026-11-03; it was never a translation.
Those stale builds were removed, and `build_manual.py --translation` now refuses a self-test
package.
