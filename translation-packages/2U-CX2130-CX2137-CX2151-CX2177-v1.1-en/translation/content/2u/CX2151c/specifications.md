| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (15 × 17 × 3.46 inches) |
| Rack size | 2U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, Deep Mini-ITX (6.7 × 8.2 inches), MicroATX, Deep MicroATX (10.4 × 10.5 inches) |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Three 80 mm fans |
| Liquid cooling | Not officially supported |
| Front bays | Two front-accessible 3.5-inch adapter bays for IcyDock or CRU storage devices; filler blanks (add-ons) each mount one 2.5-inch drive up to 15 mm thick |
| Expansion | Two full-height horizontal slots on a PCIe x16 riser, for one GPU up to 2.5 slots (50 mm) wide; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors. 2.7- and 2.75-slot cards are not supported |
| Storage | Front drive cage behind the external bays: two 3.5-inch drives up to 25 mm thick, one 2.5-inch SSD above them (up to 15 mm thick) and one below them (7 mm) |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Three 38 mm front fans | {{ facts.gpu_length_fans_38mm_mm }} mm |

<p class="info-note" role="note">Fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. AIO cooling is not officially supported: the three-fan Dynatron L35 interferes with the drive brackets. Not every mounting location can be used at the same time.</p>
