| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (15 × 17 × 3.46 inches) |
| Rack size | 2U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, Deep Mini-ITX (6.7 × 8.2 inches), MicroATX, Deep MicroATX (10.4 × 10.5 inches) |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Four 80 mm fans |
| Liquid cooling | Dynatron L34 2U AIO with four 80 mm fans |
| Front bays | None |
| Expansion | Two full-height horizontal slots on a PCIe x16 riser, for one GPU up to 2.5 slots (50 mm) wide; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors. 2.7- and 2.75-slot cards are not supported |
| Storage | No drive mounting locations. Use M.2 drives on the motherboard, or in a PCIe slot with an adapter |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans | {{ facts.gpu_length_baseline_mm }} mm |
| Four 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Four 38 mm front fans | {{ facts.gpu_length_fans_38mm_mm }} mm |
| Dynatron L34 AIO (radiator, four fans and fan guards) | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm.</p>
