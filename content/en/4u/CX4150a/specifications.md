| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (15 × 17 × 6.96 inches) |
| Rack size | 4U · 19-inch rack |
| Power supply | ATX up to {{ facts.psu_length_max_mm }} mm long including connectors; supported CRPS options require the appropriate mounting arrangement |
| Motherboard | Mini-ITX, MicroATX, ATX; EATX and SSI-CEB up to 12 × 10.5 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Three 120 mm fans; five with a 240 mm or six with a 360 mm push-pull radiator assembly |
| Liquid cooling | One 360 mm, one 240 mm, or two 120 mm radiators |
| Rear cooling | Optional 120 mm rear and PCIe-area fan brackets |
| Expansion | Eight full-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch SSD up to 7 mm thick, or one up to 15 mm thick, on the motherboard tray; unavailable with the rear fan bracket |
| Front bays | None |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 360 mm AIO with three 25 mm fans | {{ facts.gpu_length_fans_aio_mm }} mm |
| Asetek 360 mm AIO with six 25 mm fans | {{ facts.gpu_length_max_cooling_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm.</p>
