# 4U n- and g-series manual handoff

The four English Prototype 0.1 guides passed the manual builder's layout, image, link, and PDF checks. They are technical review drafts.

| Model | PDF pages | Local PDF | Review items |
| --- | ---: | --- | --- |
| CX4250n | 38 | `_build/unpublished/chassis/CX4250n/CX4250n-en-prototype.pdf` | — |
| CX4280n | 38 | `_build/unpublished/chassis/CX4280n/CX4280n-en-prototype.pdf` | Model-specific cover photo |
| CX4250g | 30 | `_build/unpublished/chassis/CX4250g/CX4250g-en-prototype.pdf` | Exploded-view callouts and model-specific top-view clearance drawing |
| CX4280g | 30 | `_build/unpublished/chassis/CX4280g/CX4280g-en-prototype.pdf` | Exploded-view callouts, model-specific top-view clearance drawing and cover photo, and confirmed compatibility limits |

CX4280n uses the CX4713 cover photo and clearance drawings for review. CX4280g uses the CX4250g cover photo and provisional CX4280n compatibility limits.

## Illustration and procedure decisions

- **Backplane, n series, page 31.** Facing the front of the racked chassis, count left to right from bay 1 at the end farthest from the power switch to bay 10 nearest it. J1 serves bays 1–4, J7 serves bays 5–8, and J13 serves bays 9–10 plus both front SSD SATA ports. The connector illustration looks at the backplane from inside the chassis. Use the EPS/CPU Y-cable or two PCIe adapters to power both backplane inputs. Front SSDs need separate SATA power. [Sliger retrofit FAQ for cable diagrams](https://sliger.com/faq/Front-Load%20NAS%20Backplane)
- **Backplane power cables, n series, page 32 and kit item L.** The hardware key uses a cut-out of the retrofit kit photo `illustrations/kits/kit-nas-retrofit/unedited/DSC00016.JPG`. The page after the backplane connections shows the line drawing `illustrations/kits/kit-nas-retrofit/power-cables/included-power-cables.png` (lengths and pin roles).
- **Front bays, g series, pages 22–23.** Remove the four 217-499 bank-to-subfront screws, slide the bank back, then lift it out. The device illustrations use 217-477P side-mount screws. The filler has its own illustration.
- **Cable management, all four models.** The view uses the hand-framed CX4280g camera with the aim point adjusted to each chassis. Fans and PSU are visible, and the AIO is hidden to expose the routing area. Each guide applies a green vector overlay to its own render. Find the page at 34 in the n guides and 26 in the g guides.
- **Exploded views.** The n guides have model-specific callouts. The CX4280n exploded camera was framed by hand and is separate from the 27 CX4250n-derived cameras used for the other illustrations.

## Rebuild and rerender

Run `python scripts/build_manual.py --model <model>` from the repository root with the manual build environment active. The local HTML, page overview, and validation report sit beside each PDF. Guide text, page definitions, and callout coordinates are in `content/en/4u/<model>/`. The shared backplane procedure is in `content/en/shared/rackmount/backplane-connections.md`. The builder uses publication copies in `illustrations/published/4u/<model>/`.

On the CAD workstation, the local Solid Edge scripts, step JSONs, saved cameras, and render outputs are in `scripts/solidedge/`. Full-resolution images used by the guides are staged in `illustrations/4u/<model>/`. These local CAD files are outside the Git handoff.

- Use `era_steps.py` with a step spec for ordinary renders. To adjust a view in ERA, use `era_steps.py --pose` and record it with `capture_view.py`.
- Use `render-4u-g.py` for the g-series batches, including the device-mounting views with 217-477P geometry. It takes the active model ID, followed by optional step prefixes.
- Use `render-4u-cable-management.py` to reuse the captured cable-management camera across the four assemblies in ERA. The green overlays are defined in each guide's `cable-management-highlight.json` and must be checked against any replacement render before it is imported.
