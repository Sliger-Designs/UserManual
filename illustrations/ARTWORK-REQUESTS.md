# Artwork requests

Renders and drawings still needed for the rackmount manuals. This file is updated in every
manual pull request: items move out of it when artwork arrives or a page no longer needs it.

**Supplying artwork:** put model renders in `illustrations/<2u|3u|4u>/<model>/` and shared parts
in `illustrations/common/hardware/`, keeping descriptive filenames, then say which request they
answer. Full-resolution originals stay out of Git (see [README.md](README.md)).

**Marking a row off:** once the files are in place, put `added` (or the date) in the row's
**Done** column. If only part of a row is supplied, name that part instead, for example
`added: exploded view`. The next manual pull request checks the files, uses them, and then
removes or shortens the row.

## Rules for reusing renders

Confirmed 2026-11-04:

- A render can be reused by another model when it shows the same part and view, for example
  the CX3170a XL lid render for the CX3171a. Reused renders are noted in the manual's
  inventory, and each reuse is listed in its pull request for review.
- Rack ears and pull handles are shared within each height: one 2U, one 3U and one 4U pair
  (`illustrations/common/hardware/{2U,3U,4U}{RackEars,PullHandles}.jpg`).
- 2U chassis have no motherboard tray, so they need no tray renders. 2U AIO renders may be
  supplied later; until then 2U manuals describe AIO installation in text beside a grey placeholder.
- The CX3701 and CX3702 do not use motherboard standoffs. Of their successors (website concepts),
  the CX3150n (CX3701 "v2") uses no standoffs and the CX3180n (CX3702 "v2") uses standoffs.
- The CX3151i standoff, I/O-shield, motherboard, PSU and SSD steps use the CX3151x renders
  (same riser tray and rear); its bay-bracket drive steps use the CX3150i renders.
- Each 17-inch model and its XL version are identical apart from the motherboard tray (the XL
  tray is deeper; the CX3170a XL and CX3171a XL trays carry a drive cage). Confirmed 2026-11-05.
- The 17-inch non-XL trays are the same parts as the 15-inch trays (CX3150a, CX3151a, CX3152a);
  the CX3171a and CX3172a tray steps use those renders (confirmed 2026-11-05).
- Every 3U "i" chassis has the same 5.25-inch bay bracket; bracket steps a model lacks use the
  CX3150i renders (confirmed 2026-11-05).
- The 5.25-inch bay filler blank is one part shared by every chassis with a 5.25-inch bay; all
  manuals use the same filler-blank page and renders (`illustrations/common/4u-bay-blank/`).
- Push-pull is not officially supported on the CX3150a (360 mm, six fans) or the CX3150i and
  CX3150x (240 mm, four fans), so no push-pull renders are requested for them.
- The CX4150e, CX4170e and CX4200e use the same 5.25-inch bay bracket; their bay-device steps
  share the CX4150e bracket renders (`illustrations/common/4u-bay-bracket/`).

## Published manuals: open items

| Done | Model | Needed | Effect until supplied |
|---|---|---|---|
|  | CX3150i | Optional: bay-bracket-top HDD render (as 4k) with green E screws; 4k shows blue D, while the text specifies E (2026-11-05) | The bracket-top HDD step shows blue screws |
|  | CX3150x | Optional: the cover render renamed (supplied as `_CX3150a_rendering.jpg` in the CX3150x folder) | None (optional) |
|  | CX3151a | Optional: the cover render renamed (supplied as `_CX3150a_rendering.jpg` in the CX3151a folder) | None (optional) |
|  | CX3151i | Optional: CX3151i renders for the standoff, I/O-shield, motherboard, PSU and SSD steps (the CX3151x ones are used; the CX3150i-named copies show the wrong rear) | None (optional) |
|  | CX3170a XL | Optional: AIO + fans render (the CX3172a XL 3c is used); drive-cage SSD render (the CX3150x 4d is used, magenta review dot) | None (optional) |
|  | CX3170i XL | Optional: 17-inch renders for the faceplate, rack-ear, fan, AIO and 5.25-inch bay steps (the CX3150i ones are used) | Those steps show the 15-inch chassis |
|  | CX3171a XL | Optional: XL riser-tray renders for the I/O shield, motherboard, PSU, SSD, rear cover, brace and GPU steps (the CX3151a ones are used) | Those steps show the 15-inch tray |
|  | CX3171i XL | Optional: 17-inch i and XL riser-tray renders (CX3150i, CX3151i and CX3151x ones are used) | Those steps show the 15-inch chassis |
|  | CX3172i XL | Optional: 17-inch renders for the faceplate, rack-ear, fan, AIO and bay steps (the CX3152i/CX3150i ones are used) | Those steps show the 15-inch chassis |
|  | CX3171a | Optional: 17-inch renders for the tray, riser and GPU steps (the CX3151a ones are used; magenta review dots in draft builds) | Those steps show the 15-inch chassis |
|  | CX3172a | Optional: 17-inch renders for the tray, PSU, SSD and GPU steps (the CX3152a ones are used; magenta review dots in draft builds) | Those steps show the 15-inch chassis |
|  | CX3701 | Exploded view; 92 mm AIO with the 3D-printed 120-to-92 mm adapter on the rear fan bracket. Optional: NAS front-panel render (the shared 3U "a" front drawing is used) | Exploded view omitted; the AIO page is text only |
|  | CX3702 | Exploded view. Optional: NAS front-panel render (the shared 3U "a" front drawing is used); locked-HDD render (the CX3701 one is used) | Exploded view omitted |
|  | CX4170a | Optional: external side/front dimension profiles. CRPS installation will be covered in a separate manual | None (optional) |
|  | CX4200f | Optional: the push-pull assembly installed in the three-bay CX4200f (the page shows the radiator-and-fan assembly only, CX4150e render) | None (optional) |
|  | CX4150e/i, CX4170e/i, CX4200e/f/i | Higher-resolution 4U e, f and i front I/O drawings (`common/front-io/CX4Ue_FPIO.png`, `CX4Uf_FPIO.png`, `CX4Ui_FPIO.png` are about 1000 px; interim versions supplied 2026-11-09) | None (interim drawings used) |
|  | 3U and 4U models with a 5.25-inch drive bracket | Redo the 5.25-inch drive bracket drive-installation renders (the 10a–10d steps, and the shared `common/4u-bay-bracket` images) with the current bracket revision, P/N DFB525-100E. Function is unchanged; only its appearance differs | None (the current renders show the previous bracket revision) |
|  | CX4712 | Exploded view; motherboard-tray removal and reinstallation renders (as CX4713 5a–5f; the tray is removable) | Grey placeholders on the exploded-view and tray pages |
|  | CX4713 | Exploded view; product render | Grey placeholder on the exploded-view page |

## 2U prototypes: open items

| Done | Model | Needed | Effect until supplied |
|---|---|---|---|
|  | CX2177a, CX2177c, CX2177x | Exploded views with the rack ears and pull handles (the supplied views show neither) | The part key leaves out the "Rack ear & pull handle" callout |
|  | CX2177a | AIO render: Dynatron L34 radiator with four 80 mm fans on the front fan panel | Grey placeholder on the AIO page |
|  | CX2177x | Rear drive bracket with 2.5-inch SSDs (as CX2177a step 4c) | Grey placeholder on the rear-bracket drive page |
|  | CX2177c | Top-view and front-view clearance drawings; front-panel render (`_CX2177c_FRONT`) | Grey placeholders on the clearance and front-port pages |
|  | CX2177c | Numbered step renders of the current design (the supplied renders are unnumbered and several show an earlier layout); confirm the step mapping in the draft, e.g. `_CX2177c_BRACKET INSTALL` used for the GPU and slot-cover step | The draft uses the supplied renders as mapped |
|  | CX2137a | Exploded view (none was in the CX2137a folder on 2026-11-12; the CX2137b one is `_CX2137b.jpg`) | Grey placeholder on the exploded-view page |
|  | CX2137b | Exploded view with the rack ears and pull handles; a higher-resolution exploded view (the supplied one is 1688 px wide) | The part key leaves out the rack ear & pull handle callout |
|  | CX2137a | AIO render: Dynatron L34 radiator with four 80 mm fans on the front fan panel | Grey placeholder on the AIO page |
|  | CX2151a, CX2151c, CX2151x | Exploded views with the rack ears and pull handles; higher-resolution CX2151c/x views (1688 px wide) | The part key leaves out the rack ear & pull handle callout |
|  | CX2151a | AIO render: Dynatron L34 radiator with four 80 mm fans on the front fan panel | Grey placeholder on the AIO page |
|  | CX2151a | Optional: front render named for the model (the folder holds an identical copy named `_CX2177a_FRONT.tif`, which is used) | None (optional) |
|  | CX2151x | Top-view and front-view clearance drawings; front-panel render (`_CX2151x_FRONT`); numbered step renders (confirm the mapping of the supplied unnumbered set in the draft) | Grey placeholders on the clearance and front-port pages |

## Cable management (not blocking V1)

Wanted for every rackmount manual, but no manual waits for them: until supplied, the
cable-management page is text only and refers to the cable-management bar on the top-view
clearance drawing. Supplied so far: CX3150a/i/x, CX3151a/i/x, CX3152a/i, the CX317 family (shared renders noted below), all ten 4U models and the
CX4712/CX4713 (the bar highlighted in green on the motherboard tray); the models below need an
equivalent view.

| Done | Model | Needed |
|---|---|---|
|  | CX3171a, CX3172a | Their own cable-management renders (the CX3170a render is used; blue review dot in draft builds). Not a release blocker |
|  | CX3170i XL, CX3171a XL, CX3171i XL | Their own cable-management renders (the CX3170a XL render is used; blue review dot in draft builds). Not a release blocker |
|  | CX3172i XL | Its own cable-management render (the CX3172a XL render is used; blue review dot in draft builds). Not a release blocker |
|  | CX3701, CX3702 | Cable-management bar highlighted on the tray |

Every 3U manual built later joins this list unless its render set includes the view. 2U chassis have no
motherboard tray to route cables to, so 2U manuals get no cable-management render; their page is text
only (2026-11-12).

## 3U

Every released 3U manual is built (November 5, 2026); open items are in the tables above.

## Concept models

The CX3150n, CX3180n, CX4250n and CX4280n are listed on the website as concepts ahead of
preorder. Their manuals are built once renders and specifications are available; none are
requested yet.

## 2U: not yet built

2U render sets are named and grouped differently; these are confirmed when each family is
built. No tray renders are needed (see above).

| Done | Model | Have | Needed |
|---|---|---|---|
|  | CX2130a | 10 | SSD and GPU steps (and standoffs/I/O shield if not shown in the motherboard renders); clearance drawings; cover render; front-panel render |
|  | CX2130c | 18 | Standoffs/I/O shield, SSD and GPU steps; clearance drawings; cover render; front-panel render |
|  | CX2130x | none | Everything |
