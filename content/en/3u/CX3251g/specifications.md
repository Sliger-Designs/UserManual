| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (25 × 17 × 5.22 inches) |
| Rack size | 3U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, MicroATX, ATX; SSI-CEB and EATX up to 12 × 10.5 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Cooling | Mid-chassis fan bracket: three 120 mm fans, up to 38 mm thick |
| Liquid cooling | One 360 mm, one 240 mm, or two 120 mm radiators |
| Rear cooling | Optional PCIe fan adapters |
| Front bays | Six 5.25-inch bays (two columns of three); two filler blanks included |
| Front I/O | Two USB 3.0 Type-A; one USB 3.2 Type-C 10 Gbps; 16 mm power switch with status light |
| Expansion | Three full-height horizontal PCIe slots with a PCIe 5.0 x16 riser; GPU up to {{ facts.gpu_height_max_mm }} mm tall including power connectors and 72 mm (3.5 slots) wide, on a support brace |
| Storage | Tray: two SSDs up to 7 mm thick, or one up to 15 mm. Each filler blank: four 2.5-inch SSDs, or one 3.5-inch HDD and two SSDs. In all: {{ facts.ssd_2_5_max }} × 2.5-inch or {{ facts.hdd_3_5_max }} × 3.5-inch |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 360 mm AIO with three 25 mm fans | {{ facts.gpu_length_fans_aio_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. Six-fan push-pull is not officially supported (the fans touch the motherboard tray); other radiator and fan combinations require a clearance check. Not every mounting location can be used at the same time.</p>
