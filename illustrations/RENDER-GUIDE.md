# Render guide: views, angles and colours for the manuals

This guide is for anyone producing manual artwork straight from the CAD models, including an
AI agent driving the CAD program. It explains what views a chassis manual uses, how each view
is framed, and the colour and shading scheme, so new renders match the ones already in the
manuals and can be dropped in without editing.

- **What is still missing, per model:** [ARTWORK-REQUESTS.md](ARTWORK-REQUESTS.md). That file
  is the live list; the summary in [section 6](#6-what-each-manual-still-needs) is a snapshot.
- **How the renders are processed afterwards:** [README.md](README.md).
- **Best reference sets to copy:** `4u/CX4170a/` (the most complete 4U set) and `3u/CX3150a/`
  (the most complete 3U set). When in doubt, match these.

Older printed manuals and their screw keys are out of date in places; where they disagree with
this guide, this guide and the current renders are right (see [section 7](#7-where-older-manuals-are-wrong)).

## 1. The CAD source

The models are Solid Edge assemblies. Most chassis have a dedicated manual assembly next to
their renders in Sliger's image library (not in Git):

| Model folder | Manual assembly |
|---|---|
| `3u/CX3150a/` | `_CX3150a_usermanual.asm` + `.cfg` (also holds CX3150x, CX3151 and CX3152 configurations) |
| `3u/CX3150i/`, `CX3150x/`, `CX3151a/`, `CX3151i/`, `CX3151x/` | `_<model>_Usermanual.asm` + `.cfg` |
| `3u/CX3702/` | `_CX3702_Usermanual.asm` + `.cfg` |
| `4u/CX4712/` | `_CX4712-A_Usermanual.asm` + `.cfg` (also holds CX4612 configurations) |
| `4u/CX4170e/` | `_CX4170e.asm` + `.cfg` (product assembly, no manual configurations) |
| `4u/CX4713/` | `4U BLACK BOX.par` only |

Each manual assembly's `.cfg` stores one **display configuration per manual step**, named
`<model> <STEP>`, for example `4712 LID UNSCREW`, `4712 STANDOFF`, `4712 PSU`,
`3151x IO SHIELD`, `AIO + FAN INSTALL + PULL`. Exploded hardware is set up with explode
events. Working rules:

1. Start from the nearest existing display configuration (same step, sibling model) rather
   than building a view from scratch; this keeps camera angle and part visibility consistent.
2. Save each new view as a new display configuration named `<model> <STEP>` in the same
   style, so it can be re-rendered later.
3. Don't save changes into shared part files (fasteners, PSU, motherboard, fans). If a part
   colour has to change for a render, change it in the assembly or display configuration only.
4. Models without a manual assembly (CX3170, CX3171, CX3172 families, 2U, CX4150/4200
   families, concepts) need one created from the product assembly, following the CX3150a or
   CX4712 manual assembly as the pattern.

## 2. The five kinds of artwork

Each manual uses five kinds of picture. Each has its own style.

| Kind | Used for | Style | Example |
|---|---|---|---|
| **Step render** | Every installation step | White line art, focus part orange, fasteners colour-coded | `5a_CX4170a_STANDOFF INSTALL.jpg` |
| **Overview ("corner") render** | Layout overviews, cooling options | Full colour, colour-coded components, black chassis exterior | `3_CX4170a_CORNER.jpg` |
| **Product render** | Cover, exploded view | Realistic shaded, black powder-coat, silver interior | `_CX4170a_rendering.jpg`, `_CX3150a_exploded.jpg` |
| **Orthographic front / rear** | Front-port and rear-panel callouts | Straight-on, no perspective, no text | `_CX4170a_FRONT.tif`, `_CX4170a_REAR.tif` |
| **Dimension drawing** | Clearance pages | Orthographic top/front, pastel component blocks, blue dimensions | `_CX4170a_ADVANCED_TOP VIEW.jpg` |

### 2.1 Step renders (most of the requests)

- **Chassis and context parts:** white faces with thin, dark-grey silhouette and edge lines
  (hidden lines off). Some faces carry the faint cool lilac tint that Solid Edge's default
  white produces (about `#F3F1F9`); keep it, don't fight it.
- **Focus part of the step: solid orange.** Lit faces about `#F8A000`, shaded faces about
  `#B85800`. Only the part being installed, removed or moved in that step is orange (lid,
  tray, drive bracket, radiator and fans, SSD, faceplate, rack ear).
- **Parts from earlier steps** that the reader needs to see for orientation stay as white
  line art (or light grey). Don't colour them.
- **A second highlight**, when a step points at a feature rather than a part (for example the
  cable-management bar), is **pale green** (about `#C8F0C8`) on top of an orange or white
  scene; see `3u/CX3150a/CABLE_MANAGEMENT_BAR_HIGHLIGHT.jpg`.
- **Fasteners** are shown in their kit colour (table below), pulled out along the insertion
  axis, with a thin grey-blue trail line from each fastener to its hole. Show every fastener
  the step uses, not just one.
- No text, numbers, letters, arrows or callouts in the image. Step numbers and hardware
  letters are added later as translatable vector overlays. The only lettering allowed is
  what's moulded or printed on the real part (for example the form-factor marks on the tray).

### 2.2 Hardware colour code (shared rackmount screwbag SBAG-HWKIT)

Every rackmount manual uses one hardware key. Use these colours in every step render:

| Letter | Fastener | Render colour | Typical use |
|---|---|---|---|
| A | 6-32 × 1/4" hex screw (217-499) | **Yellow** | Motherboard, PSU, HDDs, PCIe brackets |
| B | M3 × 0.5, 5 mm (217-621) | **Red** | 2.5" SSDs, some 3.5" accessories |
| C | 6-32 hex standoff (217-734) | **Teal / cyan** | Motherboard standoffs in the tray |
| D | M3, 5 mm thread (217-477P) | **Blue** | 2.5" SSDs, some 3.5" accessories |
| E | 6-32 × 1/4" flat-head (217-019) | **Green** | Motherboard tray, sub-front, internal brackets, front I/O bracket, countersunk drive spots |
| F | M4 × 7 mm (217-720K) | **Pink** | Rack ears and pull handles |

**Teal is also used outside the screwbag:** fan screws and radiator screws (the long ones)
are teal in the renders, the same colour as the C standoffs. The CX3151-GPUKIT screw K
(217-349, 6-32 × 1") is teal too.

Item G (slot covers), H (rack ears) and I (pull handles) are drawn as parts, not
colour-coded screws.

**Match the screw to the text, not to an older render.** For example, the CX3150i
bracket-top HDD step must show green E screws; the existing render shows blue D and is
listed as a request for exactly that reason.

### 2.3 Overview ("corner") renders

These show a fully built chassis from above, lid off, to explain the layout and cooling
options (for example `CORNER`, `CORNER 180`, `CORNER 240mm`, `CORNER 360mm DRIVE`).
Shaded (not line art), and every component type has a fixed colour:

| Component | Colour (approx.) |
|---|---|
| Chassis exterior, faceplate, rack ears | Black / charcoal `#282828` |
| Chassis interior | Light grey / silver |
| Motherboard | Green `#58A050` |
| GPU / PCIe cards | Purple `#A060B8` |
| Power supply | Blue `#3078E8` |
| SSDs and drives | Yellow |
| Fans | Red, with dark frames |
| Radiator / AIO (when not the focus) | Orange-red bar along the fan wall |

### 2.4 Product renders

Realistic material shading: black powder-coated steel, silver/zinc interior, no colour
coding. Used for the cover (`_<model>_rendering.jpg`, three-quarter front view, lid on, ears
fitted) and the exploded view (`_<model>_exploded.jpg`: lid lifted straight up, faceplate and
its filter foam pulled straight forward, rack ears pulled out sideways, the rest assembled;
see `3u/CX3150a/_CX3150a_exploded.jpg`).

### 2.5 Orthographic front and rear

Exactly square-on, orthographic (no perspective), whole chassis in frame with a small
margin, no text. Front: faceplate fitted, front I/O visible. Rear: in overview colours
(PSU blue, motherboard I/O area green, slot covers fitted). These are used for measured
callouts, so after a manual is built, a new version must keep the same framing or the
callouts have to be re-measured. Supply as `.tif`.

### 2.6 Dimension drawings

Top view and front view, orthographic, with the components as flat pastel blocks (pink GPUs,
yellow PSU/drive area, green motherboard area) and dimension lines and labels in blue. These
are the one place text is accepted in the image. Follow `_CX4170a_ADVANCED_TOP VIEW.jpg` and
`_CX4170a_ADVANCED_FRONT VIEW.jpg`.

## 3. Camera angles

All step and overview renders are **elevated three-quarter views from above**, roughly
30–40° down, perspective off (isometric-like), with the lid removed unless the step is
about the lid. Two families of angle are used, and siblings must use the same ones so that
renders can be shared:

| View | Camera | Used for |
|---|---|---|
| **Standard** | Over a front corner, looking back into the chassis | Most steps: fans, faceplate, standoffs, motherboard, GPU, drive bracket |
| **"180"** | The standard view turned 180° about the vertical axis (over a rear corner, looking forward) | Steps where the rear is the action: PSU, I/O shield, rear SSD, the second standoff view; also `CORNER 180` |
| **Rear, outside** | Elevated, behind the chassis | Lid unscrew (the lid screws are at the rear), lid slide back, tray unscrew |
| **Front, outside** | Low three-quarter front | Faceplate removal, rack ears and pull handles, product render |
| **Close-up** | Same direction as the step it details, zoomed on the part | Small parts (SSD screws, bracket screws); keep enough chassis in frame to locate it |

Frame the subject so it fills most of the image with an even margin; don't crop the
fasteners or their trail lines.

## 4. Output format

| Property | Value |
|---|---|
| Size | Step and overview renders about **5200 × 3700 px** (landscape, about 1.4:1). Front/rear about 7000 px wide. Product render about 4800 × 3400 px |
| Background | **Flat RGB (250, 252, 251)** (`#FAFCFB`), the Solid Edge default. Pure white is also fine. No gradient (turn off the assembly's gradient backgrounds), no floor, no shadow, no reflection, no vignette |
| Format | `.jpg` at high quality for step, overview and product renders; `.tif` for front/rear |
| Anti-aliasing | On |
| Text | None (except dimension drawings) |

The processing script turns everything within 4 levels of the background colour to white,
so the background must be truly flat. A gradient or shadow survives as a grey smear.

## 5. File naming and delivery

Name files the way the existing sets do. The step number and letter give the order in the
manual, and the words describe the view:

```
<step><letter>_<MODEL>_<VIEW IN CAPS>.jpg     1a_CX4170a_LID UNSCREW.jpg
                                              5b_CX4170a_STANDOFF INSTALL 180.jpg
_<MODEL>_FRONT.tif   _<MODEL>_REAR.tif        orthographic front / rear
_<MODEL>_rendering.jpg                        cover product render
_<MODEL>_exploded.jpg                         exploded view
<n>_<MODEL>_CORNER <variant>.jpg              overview renders
_<MODEL>_ADVANCED_TOP VIEW.jpg                dimension drawings
```

Use the model's exact casing (`CX4150e`, `CX3170a XL`). Put renders in
`illustrations/<2u|3u|4u>/<model>/` (shared parts in `illustrations/common/…`), then put
`added` (or `added: <which part>`) in the row's **Done** column in
[ARTWORK-REQUESTS.md](ARTWORK-REQUESTS.md). Don't overwrite an existing render; if one is
replaced, give the new one a distinct name and say which it replaces.

## 6. What each manual still needs

Snapshot of 2026-11-05. [ARTWORK-REQUESTS.md](ARTWORK-REQUESTS.md) is the authority.

### 6.1 The standard shot list

A complete rackmount chassis manual uses the following. A "shared" view is reused from a
sibling or from `common/`, so it doesn't need to be rendered again.

| # | View | Kind | Notes |
|---|---|---|---|
| 1a–1c | Lid unscrew, slide back, remove | Step, rear outside | Lid orange; rear lid screws yellow A |
| 2 | Faceplate remove (+ exploded with filter foam) | Step, front outside | Faceplate orange |
| 3a–3c | Fan install; fan + radiator (pre-cooler); fan + AIO; pull fans | Step, standard | Radiator and fans orange; fan and radiator screws teal. One set per supported radiator size |
| — | Push-pull | Step, standard | Only where push-pull is supported (not CX3150a/i/x) |
| 4a–4c | Standoffs: install, install 180, installed | Step, standard + 180 | Teal C, trail lines to every hole |
| 5 | I/O shield, then motherboard | Step, 180 / standard | Shield or board orange; yellow A |
| 6 | PSU | Step, 180 | PSU orange, yellow A |
| 7 | SSD(s), every supported SSD spot | Step, 180 / close-up | SSD orange, red B or blue D as the text says |
| 8 | GPU | Step, standard | GPU orange, yellow A in the slot brackets |
| 9 | Rack ears / pull handles | Step, front outside | Ear orange, pink F |
| 10a–f | Motherboard tray: unscrew, slide back, remove, install ×3 | Step | Only chassis with a removable tray (not 2U). Tray orange, green E |
| — | Drive bracket / drive cage: unscrew, remove, drives, reinstall | Step | 5.25" bay bracket is shared per family (see ARTWORK-REQUESTS rules) |
| — | Radiator / drive-cage clearance (interference, no interference) | Step | As CX4170a `4c1`/`4c2` |
| — | Cable-management bar highlighted | Step | Bar pale green on the tray; not blocking |
| — | Corner overviews | Overview | One per cooling layout |
| — | Front, rear | Orthographic | Required for front-port and rear-panel pages |
| — | Cover render, exploded view | Product | |
| — | Top and front dimension drawings | Dimension | Clearance pages |

Always shared, never re-rendered per model: hardware fasteners, rack ears and pull handles
per height (`common/hardware/{2U,3U,4U}{RackEars,PullHandles}.jpg`), the 5.25" bay filler
blank (`common/4u-bay-blank/`), the CX4150e/4170e/4200e bay bracket
(`common/4u-bay-bracket/`), and the 3U "i" bay bracket (CX3150i renders).

### 6.2 Published manuals: open items

| Model | Needed |
|---|---|
| CX3150i | Exploded view; bracket-top HDD with **green E** screws (current shows blue) |
| CX3150x, CX3151a | Exploded view; cover render under the right file name |
| CX3151i | Exploded view; optionally its own standoff, I/O shield, motherboard, PSU and SSD renders (CX3151x ones are used now) |
| CX3151x, CX3152a, CX3152i, CX4150a, CX4713 | Exploded view (CX4713 also a product render) |
| CX4150e, CX4170e, CX4200e, CX4200f | Push-pull, 240 mm radiator, four fans (CX4150e also an exploded view) |
| CX4150i, CX4170i, CX4200i | Push-pull, 360 mm radiator, six fans (CX4150i also an exploded view). CX4170i and CX4200i also radiator/drive-cage clearance and a 5.25" device in the bay bracket |
| CX4200a | Exploded view; radiator/drive-cage clearance |
| CX4712 | Exploded view; motherboard-tray removal and reinstallation (as CX4713 5a–5f) |
| CX4170a | Optional: external side/front dimension profiles |
| Every rackmount model | Cable-management bar highlighted (not blocking) |

### 6.3 Manuals not built yet

| Model | Have | Needed |
|---|---|---|
| CX3170a, CX3170i XL, CX3171a, CX3171a XL, CX3171i XL, CX3172a, CX3172i XL | 7–17 renders each | The installation-step set (6.1) and a cover render. Shared steps may come from the XL sibling |
| CX3170a XL, CX3172a XL | 37–48 | Push-pull, cover render |
| CX3701 | 42 | AIO renders, front-panel render (no standoffs: skip 4a–4c) |
| CX3702 | 44 | Front-panel render (no standoffs) |
| 2U (CX2130, CX2137, CX2151, CX2177 families) | 0–31 each | Varies; no tray renders are ever needed for 2U. See ARTWORK-REQUESTS |
| Concepts (CX3150n, CX3180n, CX4250n, CX4280n) | none | Full set once specifications are final. CX3150n uses no standoffs, CX3180n does |

## 7. Where older manuals are wrong

Someone working only from older manuals and loose renders should know:

- **Screw key:** older checklists list cyan standoff, yellow 6-32, blue M3 × 8, pink M4 × 7
  and red M3 × 5, with no green. The current key is A–F in [section 2.2](#22-hardware-colour-code-shared-rackmount-screwbag-sbag-hwkit).
  Green E (6-32 flat-head) is used for trays, brackets and countersunk spots. The old item J
  (packing paper) is gone.
- **CX3151 GPU:** draw one GPU on the riser. The vertical second-GPU slot was removed
  (2025-03-22); renders showing two GPUs are out of date.
- **Push-pull** isn't supported on the CX3150a, CX3150i or CX3150x; don't render it.
- **Colours in some supplied renders are wrong** (notably some CX3151 renders, where parts
  have the wrong purple or green). Use the colour rules above rather than copying a
  neighbouring render.
- **2U chassis have no motherboard tray**, and the CX3701 and CX3702 use no standoffs.

## 8. Checklist before handing over a render

- [ ] It's the view named in ARTWORK-REQUESTS, for the right model and radiator size.
- [ ] Only the focus part is orange; context is white line art; fasteners are in kit colours
      that match the manual text.
- [ ] Same camera family as the sibling renders (standard, 180, rear, front).
- [ ] Flat `#FAFCFB` or white background; no gradient, shadow or floor.
- [ ] No text, arrows or callouts (except dimension drawings).
- [ ] About 5200 × 3700 px, named in the existing pattern, saved in the model folder.
- [ ] Display configuration saved as `<model> <STEP>`; no shared part files modified.
- [ ] Row marked `added` in ARTWORK-REQUESTS.
