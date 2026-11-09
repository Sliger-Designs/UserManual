| Item | Supported configuration |
|---|---|
| Motherboards | Mini-ITX, MicroATX and ATX; EATX with PSU at front or on side fan bracket |
| Rear ATX PSU | Limits motherboard size to ATX |
| PSU | ATX, SFX and SFX-L |
| CPU cooler height | {{ fact('air_cooler_height_max_mm') }} mm maximum |
| PCIe slots | {{ fact('pcie_slots') | replace('x Full Height', '') }} full-height slots; five painted covers supplied |
| PCIe card height | {{ fact('gpu_height_max_mm') }} mm maximum |
| Card length | {{ fact('gpu_length_baseline_mm') }} mm maximum; {{ fact('gpu_length_fans_only_mm') }} mm with two 25 mm front fans |
| Radiator mounting | Up to 360 mm at top, bottom or side; 240 mm at front; 120 mm at rear |
| Side fan bracket | Second bracket supported; purchased separately |
| Front I/O | One USB-A, one USB-C and one power/status switch |
| Storage | Optional shared S6xx SSD/HDD brackets at fan mounting locations |

<p class="info-note" role="note">Available combinations depend on installed components. Verify the actual EATX board envelope and connector space; an EATX label alone does not establish a universal board size.</p>
