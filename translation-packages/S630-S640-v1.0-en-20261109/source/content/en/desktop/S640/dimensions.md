### Chassis dimensions

| Measurement | Overall | Internal |
|---|---|---|
| Depth | {{ fact('outer_dimensions_mm')['depth'] }} mm | {{ fact('internal_dimensions_mm')['depth'] }} mm |
| Width | {{ fact('outer_dimensions_mm')['width'] }} mm | {{ fact('internal_dimensions_mm')['width'] }} mm |
| Height | {{ fact('outer_dimensions_mm')['height'] }} mm | {{ fact('internal_dimensions_mm')['height'] }} mm |

S630 and S640 share the same depth and width; S640 is taller.

### Component clearance

| Item | Maximum |
|---|---|
| CPU cooler height | {{ fact('air_cooler_height_max_mm') }} mm |
| PCIe card height | {{ fact('gpu_height_max_mm') }} mm |
| Card length | {{ fact('gpu_length_baseline_mm') }} mm |
| Card length with two 25 mm front fans | {{ fact('gpu_length_fans_only_mm') }} mm |

<p class="info-note" role="note">Check the actual PSU, cooling and storage arrangement. Allow room for card power connectors, cable bends and radiator/fan stacks; the options do not imply simultaneous fit.</p>
