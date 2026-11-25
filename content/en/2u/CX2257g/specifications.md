| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (25 × 17 × 3.46 inches) |
| Rack size | 2U · 19-inch rack |
| Power supply | FlexATX, up to {{ facts.psu_length_max_mm }} mm long |
| Motherboard | Mini-ITX, Deep Mini-ITX, FlexATX, MicroATX, Deep MicroATX, ATX; EATX and SSI-CEB up to 12 × 10.5 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Cooling | Four 80 mm fans on the mid-chassis fan wall, up to 38 mm thick |
| Liquid cooling | Dynatron L34 2U AIO (320 mm radiator, four 80 mm fans) on the fan wall |
| Front bays | Four 5.25-inch bays (two columns of two); two filler blanks included |
| Expansion | Seven half-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | Rear drive cage: five 7 mm SSDs, or two 3.5-inch HDDs up to 20 mm, or one HDD and one 15 mm SSD. Each filler blank: four 2.5-inch SSDs, or one 3.5-inch HDD and two SSDs. In all: {{ facts.ssd_2_5_max }} × 2.5-inch or {{ facts.hdd_3_5_max }} × 3.5-inch |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No fans | {{ facts.gpu_length_baseline_mm }} mm |
| Four 25 mm fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Four 38 mm fans | {{ facts.gpu_length_fans_38mm_mm }} mm |
| Dynatron L34 AIO (radiator and four fans) | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. Not every mounting location can be used at the same time.</p>
