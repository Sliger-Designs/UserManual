| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (15 × 17 × 5.22 inches) |
| Rack size | 3U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, MicroATX, ATX; SSI-CEB and EATX up to 12 × 10.5 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Two 120 mm fans; up to 38 mm thick |
| Liquid cooling | One 240 mm or one 120 mm radiator; radiator length up to 277 mm |
| Rear cooling | Optional PCIe fan adapters |
| Front bays | None; internal drive bracket |
| Expansion | Three full-height horizontal PCIe slots with a PCIe 5.0 x16 riser; GPU up to {{ facts.gpu_height_max_mm }} mm tall including power connectors and 72 mm (3.5 slots) wide, on a support brace |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch and {{ facts.hdd_3_5_max }} × 3.5-inch mounting locations: eight 2.5-inch or three 3.5-inch in the drive bracket (or mixed layouts); two 2.5-inch on the motherboard tray (7 mm, or one 15 mm) |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Two 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 240 mm AIO with two 25 mm front fans | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. Four-fan push-pull is not officially supported. Not every mounting location can be used at the same time.</p>
