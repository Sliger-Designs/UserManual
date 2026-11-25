| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (17 × 17 × 3.46 inches) |
| Rack size | 2U · 19-inch rack |
| Power supply | FlexATX, up to {{ facts.psu_length_max_mm }} mm long |
| Motherboard | Mini-ITX, Mini-DTX, FlexATX, MicroATX, ATX, EATX and SSI-CEB up to 12 × 10.5 inches; SSI-EEB up to 12 × 13 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Three 80 mm fans, up to 38 mm thick |
| Liquid cooling | Not officially supported |
| Front bays | Two front-accessible 3.5-inch adapter bays for IcyDock or CRU storage devices |
| Expansion | Seven half-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch and {{ facts.hdd_3_5_max }} × 3.5-inch mounting locations: in the front drive cage, two 3.5-inch drives up to 25 mm thick, one SSD above them up to 15 mm thick and one below them, 7 mm; five 7 mm SSDs in the rear drive bracket when the 3.5-inch HDD mounts are unused |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Three 38 mm front fans | {{ facts.gpu_length_fans_38mm_mm }} mm |

<p class="info-note" role="note">Fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. SSI-CEB and 10.5-inch deep EATX motherboards are incompatible with 38 mm thick fans. AIO cooling is not officially supported: the three-fan Dynatron L35 interferes with the drive brackets. Not every mounting location can be used at the same time.</p>
