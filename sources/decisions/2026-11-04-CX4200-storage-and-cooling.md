# CX4200a / e / f / i storage and cooling — November 4, 2026

## Storage: total mounting locations

Counted as for the CX4150 and CX4170 models: the rear motherboard-tray mounting (two 7 mm
SSDs or one 15 mm SSD), each 5.25-inch bay filler blank (two 2.5-inch SSDs and one 3.5-inch
HDD), and the internal drive cage where fitted (eight 7 mm SSDs or three 3.5-inch HDDs).

| Model | Cage | Bays | 2.5-inch locations | 3.5-inch locations |
|---|---|---|---|---|
| CX4200a | yes | 0 | 10 (tray 2 + cage 8) | 3 (cage) |
| CX4200e | no | 2 | 6 (tray 2 + 2 per blank) | 2 |
| CX4200f | no | 3 | 8 (tray 2 + 2 per blank) | 3 |
| CX4200i | yes | 1 | 12 (tray 2 + cage 8 + blank 2) | 4 (cage 3 + blank 1) |

The CX4200a, CX4200e and CX4200f totals match the spec review. The CX4200i 3.5-inch total
is 4 (cage 3 + blank 1), confirmed over the spec review's 5, as for the CX4170i.

## Cooling and GPU length

- CX4200a and CX4200i: as the CX4170a and CX4170i. 360 mm push-pull with six fans
  (398 mm GPU) is supported only with the drive cage removed; 360 mm radiators over 27 mm
  thick interfere with the cage.
- CX4200e: as the CX4170e (two fans, 240 mm AIO at most); GPU 475 / 450 / 422 / 398 mm.
- CX4200f: two fans on a removable front fan bracket, 240 mm AIO at most; GPU limits are
  shorter because of the third bay: 424 / 398 / 371 / 347 mm (spec review, matching the
  website and import sheet).
- All four: ATX PSU up to 268 mm including connectors.

## Bay bracket and device screws

- The CX4200e uses the same 5.25-inch dual-bay bracket as the CX4150e and CX4170e; its
  bay-device steps use the shared bracket renders (`illustrations/common/4u-bay-bracket/`).
- CX4200f with a 240 mm AIO: the radiator comes close to the screws retaining 5.25-inch
  devices without touching them. Countersunk screws are recommended in that position:
  B (217-621) for M3 threads, E (217-019) for 6-32.

## Unused renders

`CX4200f-0.jpg` to `CX4200f-4.jpg`, and the CX4200a `STANDOFFDIMS` image and screenshots,
are not needed in the manuals.
