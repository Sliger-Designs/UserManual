# CX3150a / CX3150i / CX3150x storage and cooling — November 5, 2026

## Motherboard-tray SSD mounting

Confirmed: the motherboard tray of every 15-inch 3U chassis (CX3150a, CX3150i, CX3150x) has the
same 2.5-inch mounting between the motherboard I/O shield and the SFX PSU cutout: two SSDs up
to 7 mm thick, or one SSD up to 15 mm thick, each secured with red B screws. This follows the
CX3150i website wording; the CX3150a and CX3150x pages ("one 2.5-inch drive up to 15 mm") list
only the 15 mm case.

## Storage: total mounting locations

Drive counts lead with total mounting locations. Not every location can be used at the same
time.

| Model | 2.5-inch locations | 3.5-inch locations |
|---|---|---|
| CX3150a | 2 (tray) | 0 |
| CX3150i | 9 (tray 2 + filler blank 4 + bay bracket top 2 + under the bay bracket 1) | 2 (filler blank 1 + bay bracket top 1) |
| CX3150x | 10 (tray 2 + drive bracket 8) | 3 (drive bracket) |

CX3150i positions, as rendered (`illustrations/3u/CX3150i/`):

- 5.25-inch bay filler blank: four 2.5-inch SSDs (4e), two 15 mm SSDs (4f), or one 3.5-inch HDD
  through its bottom holes (4g). The bay holds the filler blank or a 5.25-inch device, not both.
- Top of the 5.25-inch bay bracket: two 2.5-inch SSDs (4j) or one 3.5-inch HDD (4k).
- Under the 5.25-inch bay bracket: one 2.5-inch SSD, usable with a 5.25-inch device fitted (4h).

CX3150x drive bracket: eight 2.5-inch SSDs; or two 3.5-inch HDDs and three SSDs; or one HDD and
five SSDs; or three HDDs (website).

These totals replace the spec review's CX3150i "4 × 2.5-inch, 1 × 3.5-inch", CX3150x
"9 × 2.5-inch" and CX3150a "1 × 2.5-inch".

## HDD screws on the CX3150i filler blank and bay bracket

Renders 4g (purple screws, not a kit colour) and 4k (blue D, M3) do not match the 6-32 threads
of a 3.5-inch HDD. The manual calls for green E (6-32 flat-head), as on the 4U filler blank.

The 4g view is identical to the shared 4U render `common/4u-bay-blank/drive6.1.jpg.jpg`
(same filler blank, green E screws), and 4e matches `drive12.jpg.jpg`: the 3U and 4U filler
blanks are the same part. The CX3150i uses `drive6.1.jpg.jpg` for the HDD step. No equivalent
exists for the bay-bracket-top HDD (4k), which is used as supplied until a corrected render
arrives.

## 240 mm AIO and the 5.25-inch device screws

The CX3150i top-view drawing note ("if installing a radiator, the screws in this location will
have to be removed") marks where a 240 mm radiator can touch the screws retaining a 5.25-inch
device, as documented for the CX4150e and CX4200f. Use countersunk screws there, B (217-621)
for M3 or E (217-019) for 6-32, or leave those screws out.

## Push-pull

The 240 mm radiator with four fans (CX3150i, CX3150x) and the 360 mm radiator with six fans
(CX3150a) are not officially supported. Maximum GPU length with cooling is 296 mm (240 mm or
360 mm radiator with front fans); the 270–272 mm source candidates are not published.
