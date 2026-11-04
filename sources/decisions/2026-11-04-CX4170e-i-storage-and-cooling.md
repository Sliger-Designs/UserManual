# CX4170e / CX4170i storage and cooling — November 4, 2026

> **Superseded in part:** filler-blank capacity and 2.5-inch totals are corrected in
> `2026-11-04-bay-filler-blank-capacity.md` (four SSDs, or one HDD and two SSDs, per blank).

## Storage: total mounting locations

Counted the same way as the CX4150e/i (`2026-11-04-CX4150e-i-storage-and-cooling.md`):
the rear motherboard-tray mounting (two 7 mm SSDs or one 15 mm SSD), each 5.25-inch bay
filler blank (two 2.5-inch SSDs and one 3.5-inch HDD), and on the CX4170i the internal drive
cage (eight 7 mm SSDs or three 3.5-inch HDDs, as on the CX4170a).

| Model | 2.5-inch locations | 3.5-inch locations |
|---|---|---|
| CX4170e | 6 (tray 2 + 2 per blank, two bays) | 2 (1 per blank) |
| CX4170i | 12 (tray 2 + cage 8 + blank 2) | 4 (cage 3 + blank 1) |

The CX4170i 3.5-inch total is 4, confirmed over the spec review's 5. Not every location can
be used at the same time.

## Cooling

- CX4170i 360 mm push-pull (six fans, 322 mm GPU) is handled as on the CX4170a: supported,
  but it conflicts with the internal drive cage, which must be removed. The import sheet's
  "not officially supported" disclaimer does not apply.
- CX4170e takes up to a 240 mm AIO; as on the CX4150e, a hex-head screw retaining a
  5.25-inch device can touch the radiator, so a countersunk screw (B for M3 threads, E for
  6-32) is used in that position.

## Shared bay bracket

The CX4150e and CX4170e use the same 5.25-inch bay bracket. The CX4170e bay-device steps
therefore use the CX4150e bracket renders, shared in `illustrations/common/4u-bay-bracket/`.
