| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (17 × 17 × 3.46 inches) |
| Rack size | 2U · 19-inch rack |
| Power supply | FlexATX, up to {{ facts.psu_length_max_mm }} mm long |
| Motherboard | Mini-ITX, Mini-DTX, FlexATX, MicroATX, ATX, SSI-CEB; SSI-EEB up to 12 × 13 inches; XL-ATX/EATX up to 12.8 × 13 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Four 80 mm fans, up to 38 mm thick |
| Liquid cooling | Dynatron L34 2U AIO with four 80 mm fans |
| Front bays | None |
| Expansion | Seven half-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch and {{ facts.hdd_3_5_max }} × 3.5-inch mounting locations in the rear drive bracket: five 7 mm SSDs; or two 3.5-inch HDDs up to 20 mm thick; or one 3.5-inch HDD and one 2.5-inch SSD up to 15 mm thick |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans | {{ facts.gpu_length_baseline_mm }} mm |
| Four 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Four 38 mm front fans | {{ facts.gpu_length_fans_38mm_mm }} mm |
| Dynatron L34 AIO (radiator and four fans) | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. Not every mounting location can be used at the same time.</p>
