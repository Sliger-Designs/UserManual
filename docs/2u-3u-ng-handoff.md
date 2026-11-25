# 2U and 3U n/g manuals and clearance drawings: handoff (2026-11-25)

All work is on branch `ng-manuals`, **PR #63** (open, Prototype 0.1 manuals for the 4U and 3U n/g concepts and the
CX2257g). Everything below is committed and pushed. PR #65 (faceplate "aside" wording and translation packages for the
42 released manuals) is merged.

## Where each model stands

| Model | State | Still open |
| --- | --- | --- |
| CX2257g | Every view rendered from `CX2257g_INT`; top and front clearance drawings done and approved | — |
| CX3150g, CX3180g | Every step rendered from the `_INT-MIN` models, including 3c/3f fan close-ups (2026-11-25) | Top-view drawings (grey placeholder); front views (CX3701/CX3702 drawings borrowed; CX3180g has a new tray); covers (CX3701/CX3702 photos) |
| CX3150n, CX3180n | Every step rendered from the `_INT-MIN` models; backplane callouts; shared 8e key-lock render | Top and front drawings (CX3701/CX3702 borrowed); covers; HDD step 2 reuses the CX4250n render until the SA-3000n demo drives get their missing shoulder screws |
| CX3250g, CX3251g, CX3252g | Rendered; top views done earlier | Front views (CX3150a/CX3151a/CX3152a drawings borrowed); CX3251g 9e needs a slot cover in `MT3-C1A_INT-MIN`; CX3252g 7b needs the upright second SSD and its two screws in `MT3-C2A_INT-MIN` |
| CX4250g, CX4280g | See `docs/4u-ng-handoff.md` | Front drawings showing the eight 5.25-inch bays; top-view pages |
| CX4250n, CX4280n | See `docs/4u-ng-handoff.md` | Own top/front drawings (CX4712/CX4713 borrowed); CX4280n cover |

`illustrations/ARTWORK-REQUESTS.md` (Concept models table) is the running list; Sliger edits it live, so stage it by
path. Borrowed renders not listed there are intentional (4U g/n tray and fan steps from CX4712/CX4713, CX2257g drive
bracket from CX2177a, 3U g bay devices from CX3250g).

## Clearance drawings: the agreed method

Worked out on the CX2257g with Sliger, matching the website drawing
<https://sliger-part-images.s3.amazonaws.com/1371.webp>.

1. **Sliger adds PMI dimensions** in the assembly (measured CAD values: inside face of the rear panel to the closest
   blocking item). ERA renders them in purple with inch over mm.
2. **Render at `--width 4000`.** At 9000 px the PMI text is unreadable; changing HeightPMI or TextScale by script had no
   effect on ERA.
3. **Top view** spec (`make_specs_2257g.py`, `TOP_VIEW`): straight-down orthographic, lid hidden, faceplate shown,
   chassis, faceplate and screws in their own colours (no `["*", "White"]`). GPU pink, 25 mm fans red, L34 in its own
   black, HDD/SSD yellow, 5.25-inch bay devices (ICY DOCK MB994SP-4S) in **Manual Pale Yellow** (add it per document with
   `scripts/solidedge/add_manual_pale_yellow.py <prefix>`, like Manual Orange; it is lost if the document reloads
   unsaved; Tan is too orange).
4. **Front view**: Sliger hides parts by hand and frames the orthographic front; I list the hidden occurrences with
   `state_dump.py` (compare with an earlier dump), write them into a `FRONT_VIEW` spec and record the current camera into
   `cameras/<model>.json`. Sliger then shows everything again. Board own colours, GPU pink, PSU blue, drive bracket and
   drives yellow.
5. **Notes overlay**: `scripts/clearance_overlay.py scripts/clearance_specs/<model>-<top|front>.json [--preview out.png]`
   writes `content/en/<cat>/<model>/<view>-view-dimensions.json`. Notes are ALL CAPS, in the margins, with angled
   leaders landing on the dimension lines, in Sliger's website wording. Positions are pixels in `frame_px`. Re-run after
   every re-render (the overlay records the image hash). `image_callouts.py` draws `notes` (and `dimension_labels`, now
   unused); reference-drawing pages render annotated SVGs.
6. Stage the render as `illustrations/<cat>/<model>/<model>_TOP VIEW.jpg` / `_FRONT VIEW.jpg` (the name must contain
   `TOP VIEW` for the top-view layout), point the page at it with `image_annotations`, update the inventory, run
   `prepare_assets.py` and `build_manual.py`, restore `illustrations/published/common/manifest.json`, and `git rm` the
   orphaned published JPG.

Next drawings need Sliger's PMI first: CX3150g/CX3180g top views clear the last two grey boxes.

## Local CAD tooling (not in Git)

`scripts/solidedge/` is excluded from Git (`.git/info/exclude`). Spec generators: `make_specs_2257g.py`,
`make_specs_3u_g15_int.py` (the 15/18-inch g and n models from `_INT-MIN`; fan close-ups now apply to g models too).
Helper scripts copied from the session scratchpad are in `scripts/solidedge/staging/`: `stage_15g.py` (staging map for
CX3150g/CX3180g/CX3150n/CX3180n), `io_fill.py` (orange I/O-shield fill), `explode_callouts.py`, `stage2_325x.py`,
`pmi.py <model>` (lists PMI dimensions and values), `styles.py` (lists face styles). Do not run a second render while a
model is posed for framing.

## Waiting on Sliger

- PMI dimensions (and a hidden-parts setup for front views) for every remaining clearance drawing.
- Cover photos or renders: CX3150n/g, CX3180n/g, CX4280n.
- The 20 missing shoulder screws on the SA-3000n demo drives; the CX3251g slot cover; the CX3252g second SSD.
- German translator strings for the 2U v1.1 guides.
- CAD values differ from the import CSV GPU lengths (CSV 368/342/281 vs CAD 362.9/337.9/280.9 on the CX2257g); the
  CSV may need correcting before release.
