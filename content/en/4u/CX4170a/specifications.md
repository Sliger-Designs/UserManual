| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm |
| Rack size | 4U · 19-inch rack |
| Power supply | ATX; supported CRPS options require the appropriate mounting arrangement |
| Motherboard | Mini-ITX, MicroATX, ATX; EATX up to 12 × 10.5 inches; larger boards require dimensional and mounting-pattern checks |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Three 120 mm fans; six with a compatible 360 mm push-pull assembly |
| Liquid cooling | One 360 mm, one 240 mm, or two 120 mm radiators |
| Rear cooling | Optional 120 mm rear and PCIe-area fan brackets |
| Expansion | Eight full-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | Up to {{ facts.ssd_2_5_max }} × 7 mm 2.5-inch SSDs: eight in the drive cage and two on the motherboard tray (or one 15 mm SSD there; the tray positions are unavailable with the rear fan bracket). The drive cage alternatively holds {{ facts.hdd_3_5_max }} × 3.5-inch HDDs or mixed HDD/SSD layouts; see drive-cage layouts |
| Front bays | None |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 360 mm AIO with three 25 mm fans | {{ facts.gpu_length_fans_aio_mm }} mm |
| Asetek 360 mm AIO with six 25 mm fans (Push-Pull) | {{ facts.gpu_length_max_cooling_mm }} mm |

<p class="info-note" role="note"><strong>Six-fan push-pull conflicts with the internal drive cage.</strong> Mounting positions and maximum component counts are not all usable simultaneously.</p>
