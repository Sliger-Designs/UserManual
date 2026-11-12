| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (13 × 17 × 3.46 inches) |
| Rack size | 2U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, Deep Mini-ITX (6.7 × 8.2 inches), MicroATX, Deep MicroATX (10.4 × 10.5 inches) |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Three 80 mm fans, up to 38 mm thick |
| Liquid cooling | Not officially supported |
| Front bays | None (internal 3.5-inch drive cage) |
| Expansion | Five half-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | Internal drive cage: two 3.5-inch drives and two 2.5-inch drives |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Three 38 mm front fans | {{ facts.gpu_length_fans_38mm_mm }} mm |

<p class="info-note" role="note">Fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. AIO cooling is not officially supported on the three-fan models. Not every mounting location can be used at the same time.</p>
