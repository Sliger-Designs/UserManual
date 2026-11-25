| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (17 × 17 × 5.22 inches) |
| Rack size | 3U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, Deep Mini-ITX, MicroATX, Deep MicroATX, ATX, EATX, SSI-CEB; SSI-EEB up to 12 × 13 inches and XL-ATX/EATX up to 12.8 × 13 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Two 120 mm fans; up to 38 mm thick |
| Liquid cooling | One 240 mm or one 120 mm radiator; radiator length up to 277 mm |
| Rear cooling | Optional PCIe fan adapters |
| Front bays | One 5.25-inch bay with a removable filler blank |
| Expansion | Eight full-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch and {{ facts.hdd_3_5_max }} × 3.5-inch mounting locations: tray 2 (7 mm, or one 15 mm); bay filler blank 4, or one 3.5-inch plus two 2.5-inch; bay bracket top 2, or one 3.5-inch; under the bay bracket 1 |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Two 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 240 mm AIO with two 25 mm front fans | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. Four-fan push-pull is not officially supported. The bay has no filler blank while it holds a 5.25-inch device, and not every mounting location can be used at the same time.</p>
