| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (20 × 17 × 6.96 inches) |
| Rack size | 4U · 19-inch rack |
| Power supply | ATX; supported CRPS options require the appropriate mounting arrangement |
| Motherboard | Mini-ITX, MicroATX, ATX; EATX up to 12 × 10.5 inches; larger boards require dimensional and mounting-pattern checks |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Front cooling | Three 120 mm fans; six with a compatible 360 mm push-pull assembly |
| Liquid cooling | One 360 mm, one 240 mm, or two 120 mm radiators |
| Rear cooling | Optional 120 mm rear and PCIe-area fan brackets |
| Expansion | Eight full-height PCIe slots; cards up to {{ facts.gpu_height_max_mm }} mm tall including power connectors |
| Storage | {{ facts.ssd_2_5_max }} × 2.5-inch and {{ facts.hdd_3_5_max }} × 3.5-inch mounting locations: eight 2.5-inch or three 3.5-inch in the drive cage (or mixed layouts), two 2.5-inch on the motherboard tray (7 mm, or one 15 mm), and two 2.5-inch plus one 3.5-inch on the bay filler blank. Not all locations can be used at once |
| Front bays | One 5.25-inch bay with a removable filler blank |

### GPU length by cooling configuration

| Configuration | Maximum length |
| --- | --- |
| No front fans or radiator | {{ facts.gpu_length_baseline_mm }} mm |
| Three 25 mm front fans | {{ facts.gpu_length_fans_only_mm }} mm |
| Asetek 360 mm AIO with three 25 mm fans | {{ facts.gpu_length_fans_aio_mm }} mm |
| Asetek 360 mm AIO with six 25 mm fans | {{ facts.gpu_length_max_cooling_mm }} mm |

**Six-fan push-pull conflicts with the internal drive cage.** Mounting positions and maximum component counts are not all usable simultaneously.
