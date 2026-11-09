| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (15 × 17 × 6.96 inches) |
| Rack size | 4U · 19-inch rack |
| Power supply | ATX up to {{ facts.psu_length_max_mm }} mm long including connectors; supported CRPS options require the appropriate mounting arrangement |
| Motherboard | Mini-ITX, MicroATX, ATX; EATX and SSI-CEB up to 12 × 10.5 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Two 120 mm fans; four with a 240 mm push-pull radiator assembly |
| Liquid cooling | One 240 mm or one 120 mm radiator |
| Rear cooling | Optional 120 mm rear and PCIe-area fan brackets |
| Expansion | Eight full-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Front bays | Two 5.25-inch bays with removable filler blanks |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch and {{ facts.hdd_3_5_max }} × 3.5-inch mounting locations: two 2.5-inch on the motherboard tray (7 mm, or one 15 mm), and four 2.5-inch, or one 3.5-inch plus two 2.5-inch, on each bay filler blank. Not all locations can be used at once |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Two 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 240 mm AIO with two 25 mm fans | {{ facts.gpu_length_fans_aio_mm }} mm |
| Asetek 240 mm AIO with four 25 mm fans (Push-Pull) | {{ facts.gpu_length_max_cooling_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. The tray SSD positions are unavailable with the rear fan bracket, and a bay holding a 5.25-inch device has no filler blank.</p>
