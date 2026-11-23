| Component | Specification |
| --- | --- |
| Outer dimensions, D × W × H | {{ outer.depth }} × {{ outer.width }} × {{ outer.height }} mm (18 × 17 × 5.22 inches) |
| Rack size | 3U · 19-inch rack |
| Power supply | SFX or SFX-L |
| Motherboard | Mini-ITX, Deep Mini-ITX, MicroATX; mounts without standoffs. The motherboard tray slides out for assembly |
| CPU air cooler | Up to {{ facts.air_cooler_height_max_mm }} mm tall |
| Cooling | Two 120 mm fans, side vent and rear, up to 38 mm thick |
| Liquid cooling | Not supported; the space gives the motherboard more clearance to the side fan and more cable room behind the PSU |
| Expansion | Four full-height PCIe slots; cards up to {{ facts.gpu_length_baseline_mm }} mm long including the power connector and {{ facts.gpu_height_max_mm }} mm tall |
| Front bays | Ten 3.5-inch SAS/SATA hot-swap bays on a ten-port backplane (SFF-8643 data connectors) behind the magnetic faceplate |
| Storage | {{ facts.hdd_3_5_max }} × 3.5-inch hot-swap and {{ facts.ssd_2_5_max }} × 2.5-inch (up to 7 mm, behind the front I/O) mounting locations |

<p class="info-note" role="note">Data cables are not included. Hot-swap support depends on the HBA or RAID card, motherboard and operating system; a SAS controller can run SATA drives, but a SATA controller cannot run SAS drives. A 2.5-to-3.5-inch converter bracket can mount SSDs in the front bays.</p>
