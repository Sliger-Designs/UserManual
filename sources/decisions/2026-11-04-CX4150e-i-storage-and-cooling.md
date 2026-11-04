# CX4150e / CX4150i storage and cooling — November 4, 2026

## Storage: total mounting locations

Drive counts lead with total mounting locations (see `2026-11-04-CX4170a-ssd-capacity.md`).
On both models these are the rear motherboard-tray mounting (two 7 mm SSDs or one 15 mm
SSD, shared by all 4U trays; see `2026-11-04-4U-tray-ssd-mounting.md`) plus each 5.25-inch
bay filler blank, which provides mounting for two 2.5-inch SSDs and one 3.5-inch HDD
(website specification). Confirmed totals:

| Model | 5.25-inch bays | 2.5-inch locations | 3.5-inch locations |
|---|---|---|---|
| CX4150e | 2 | 6 (tray 2 + 2 per blank) | 2 (1 per blank) |
| CX4150i | 1 | 4 (tray 2 + 2 in the blank) | 1 |

Not every location can be used at the same time: a bay holding a 5.25-inch device has no
filler blank, and the tray positions are unavailable with the rear fan bracket. These
totals replace the spec review's "3 × 2.5-inch, 1 × 3.5-inch" for both models.

## CX4150i 360 mm push-pull

Confirmed supported: a 360 mm radiator with six 25 mm fans, maximum GPU length 270 mm. The
import sheet's "not officially supported" disclaimer for this configuration does not apply.

## CX4150e filler-blank HDD and 240 mm AIO screw clearance

- `drive6.1.jpg.jpg` shows a 3.5-inch HDD installed through the bottom mounting holes of a
  5.25-inch bay filler blank (green E screws, as rendered).
- `SCREW INTERFERE.jpg` shows a 240 mm AIO touching one of the screws that retain a device
  in the 5.25-inch bays. With a 240 mm AIO, use a countersunk screw in that position instead
  of a hex-head screw: 217-621 (B, M3) or 217-019 (E, 6-32), to match the device's thread. The render is not used; the requirement is stated
  on the AIO and bay-device pages.

The CX4150i needs no such note: its bay is above the AIO and fans. Its filler blank takes a
3.5-inch HDD in the same bottom-hole position as the CX4150e, so both manuals use the
shared render `common/4u-bay-blank/drive6.1.jpg.jpg`.
