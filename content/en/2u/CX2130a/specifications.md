| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (13 × 17 × 3.46 inches) |
| Rack size | 2U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, Deep Mini-ITX (6.7 × 8.2 inches), MicroATX, Deep MicroATX (10.4 × 10.5 inches) |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Four 80 mm fans, up to 38 mm thick |
| Liquid cooling | One 320 mm radiator: Dynatron L34 2U AIO with four 80 mm fans (tested and confirmed to fit) |
| Front bays | None |
| Expansion | Five half-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | One M.2/NVMe drive on the motherboard; no 2.5- or 3.5-inch mounting locations. PCIe slots can take M.2 adapters |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans | {{ facts.gpu_length_baseline_mm }} mm |
| Four 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Four 38 mm front fans | {{ facts.gpu_length_fans_38mm_mm }} mm |
| Dynatron L34 AIO (radiator, four fans and fan guards) | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm.</p>
