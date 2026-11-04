# Rackmount hardware-kit artwork and background cleanup — November 4, 2026

The owner asked for the rackmount hardware-kit page to receive the same render fixes and
larger scale as the S630/S640 manuals, and for gray render backgrounds to be removed.

## SBAG-HWKIT top and side renders

The colored screw illustrations stay. The low-resolution top and side views are replaced
with the part-numbered renders already used by the S630/S640 (see
`2026-11-02-S6xx-hardware-confirmations.md`):

| Item | Renders | Basis |
|---|---|---|
| A yellow 6-32 hex | 217-499 | Same yellow screw as S6xx A |
| B red M3 × 5 mm | 217-621 | Filename matches the rackmount B specification |
| C standoffs | 217-734 | Owner-approved standoff artwork for S6xx C |
| D blue M3 | 217-477P | Same blue-patched flange-hex screw as S6xx E |
| E green | 217-019 | Owner instruction of 2026-11-02 for rackmount kits |
| F pink M4 × 7 mm | 217-720K | Black flat-head, matching the existing F artwork |

E is renamed **6-32 × 0.25-inch flat-head screws (217-019)**, as the owner specified on
2026-11-02 for all rackmount kits; quantities are unchanged. D is relabelled **M3 screws
(5 mm thread)**: the owner confirmed that the S6xx measurement of the same screw (5 mm of
thread, 8 mm overall) applies to rackmount kits; the reference table's M3 × 6 mm is the MRP
value.

The hardware page uses the S630/S640 sizes for screws with top/side views.

## Background cleanup

The CX4150a, CX4170a and CX3150a renders and the shared 4U rack ear use a flat background of RGB
(250, 252, 251). Pixels within 4 levels per channel of that color are replaced with white;
every other pixel, the dimensions and the framing are preserved. This is the non-AI method
the owner authorized for the S630/S640 (`2026-11-02-SFF-render-cleanup.md`). Originals and
their inventory hashes are unchanged; settings are recorded in each inventory entry.

Rackmount publication copies of cleaned renders are JPEG (quality 90, subsampling 0) to keep
the repository small, as the owner approved. S630/S640 copies remain lossless PNG.

## Rack ears and pull handles

The current rack-ear image shows an ear with a pull handle attached. The owner will supply
separate left/right rack-ear and left/right pull-handle renders for each form factor;
until then each rackmount manual lists them as missing artwork (M05).
