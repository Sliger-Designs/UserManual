| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (17 × 17 × 5.22 inches) |
| Rack size | 3U · 19-inch rack |
| Power supply | ATX, up to {{ facts.psu_length_max_mm }} mm long including connectors |
| Motherboard | Mini-ITX, Deep Mini-ITX, MicroATX, Deep MicroATX, ATX, EATX, SSI-CEB; SSI-EEB up to 12 × 13 inches and XL-ATX/EATX up to 12.8 × 13 inches. The PSU limits ATX and larger boards to five PCIe slots |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Three 120 mm fans; up to 38 mm thick |
| Liquid cooling | One 360 mm, one 240 mm, or two 120 mm radiators |
| Rear cooling | Optional PCIe fan adapters |
| Front bays | None |
| Expansion | Five full-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch mounting locations on the motherboard tray: one under the PSU and one beside the motherboard |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 360 mm AIO with three 25 mm front fans | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. Six-fan push-pull is not officially supported. Not every mounting location can be used at the same time.</p>
