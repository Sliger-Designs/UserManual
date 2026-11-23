The backplane is preinstalled. Shut down the system and unplug the PSU before connecting or reseating any cables.

### 1. Connect the controller

Use internal **SFF-8643 (Mini-SAS HD)** cables at the backplane. Match the other ends to your HBA, RAID card, or motherboard. Data cables are sold separately.

**Facing the front of the racked chassis**, count bays from left to right. Bay 1 is farthest from the power switch and bay 10 is closest. The illustration shows the backplane from inside the chassis.

| Board label | Drives served |
| --- | --- |
| J1 | Bays 1–4 |
| J7 | Bays 5–8 |
| J13 | Bays 9–10 + both front SSD SATA ports |

### 2. Power both backplane inputs

One 4-pin input powers bays 1–5 and the other powers bays 6–10. Choose one of the included {{ hw('L') }} options.

- **EPS/CPU:** Connect the Y-cable to an 8-pin EPS/CPU lead. Plug a 4-pin branch into each backplane input.
- **PCIe:** Connect both adapters to 6-pin PCIe leads. Plug one adapter into each backplane input.

Connect the adapters to the PSU harness leads. Never plug them directly into the PSU’s modular sockets.

### 3. Connect optional front SSDs

The two SATA ports sit at the power-button end of the backplane. Use a short SATA data cable for each front SSD and connect SATA power separately. Both ports carry their data to the controller through **J13**.

At startup, verify drive detection. SAS drives require a SAS controller. Check controller and operating system support before hot-swapping.

[Cable diagrams in the Sliger retrofit FAQ](https://sliger.com/faq/Front-Load%20NAS%20Backplane)
