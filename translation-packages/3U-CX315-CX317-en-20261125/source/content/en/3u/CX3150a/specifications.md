| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm |
| Rack size | 3U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, MicroATX, ATX; SSI-CEB and EATX up to 12 × 10.5 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Three 120 mm fans; up to 38 mm thick |
| Liquid cooling | One 360 mm, one 240 mm, or two 120 mm radiators |
| Rear cooling | Optional PCIe fan adapters |
| Front bays | None |
| Front I/O | Two USB 3.0 Type-A; one USB 3.2 Type-C 10 Gbps; 16 mm power switch with status light |
| Expansion | Eight full-height PCIe slots |
| GPU/card height | Up to {{ facts.gpu_height_max_mm }} mm, including power connectors |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch mounting locations on the motherboard tray: two SSDs up to 7 mm thick, or one up to 15 mm |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 360 mm AIO with three 25 mm front fans | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. Six-fan push-pull is not officially supported; other radiator and fan combinations require a clearance check. Not every mounting location can be used at the same time.</p>
