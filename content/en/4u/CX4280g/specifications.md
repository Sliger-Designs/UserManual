| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (28 × 17 × 6.96 inches) |
| Rack size | 4U · 19-inch rack |
| Power supply | ATX up to {{ facts.psu_length_max_mm }} mm long including connectors; supported CRPS options require the appropriate mounting arrangement |
| Motherboard | Mini-ITX, Mini-DTX, MicroATX, ATX, SSI-CEB; SSI-EEB up to 12 × 13 inches; XL-ATX/EATX up to 12.8 × 13 inches |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Cooling | Three 120 mm fans on the mid-chassis fan bracket; five with a 240 mm or six with a 360 mm push-pull radiator assembly |
| Liquid cooling | One 360 mm, one 240 mm, or two 120 mm radiators |
| Rear cooling | Optional 120 mm rear and PCIe-area fan brackets |
| Expansion | Eight full-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Front bays | Eight 5.25-inch bays behind the magnetic faceplate. Two filler blanks are included; the other bays take 5.25-inch devices |
| Storage | Two 2.5-inch tray mounts above the PSU cutout: two drives up to 7 mm thick, or one up to 15 mm thick. Each included filler blank holds four 2.5-inch SSDs, or one 3.5-inch HDD and two SSDs |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 360 mm AIO with three 25 mm fans | {{ facts.gpu_length_fans_aio_mm }} mm |
| Asetek 360 mm AIO with six 25 mm fans (Push-Pull) | {{ facts.gpu_length_max_cooling_mm }} mm |

<p class="info-note" role="note">Radiator thickness, fan thickness and GPU length together must be less than {{ facts.gpu_length_baseline_mm }} mm. The tray SSD positions are unavailable with the rear fan bracket.</p>

<p class="info-note" role="note">The CX4280n clearance limits are provisional for the CX4280g. Confirm them before selecting components.</p>
