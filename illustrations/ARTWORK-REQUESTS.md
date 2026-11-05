# Artwork requests

Renders and drawings still needed for the rackmount manuals. This file is updated in every
manual pull request: items move out of it when artwork arrives or a page no longer needs it.

**Supplying artwork:** put model renders in `illustrations/<2u|3u|4u>/<model>/` and shared parts
in `illustrations/common/hardware/`, keeping descriptive filenames, then say which request they
answer. Full-resolution originals stay out of Git (see [README.md](README.md)).

## Rules for reusing renders

Confirmed 2026-11-04:

- A render can be reused by another model when it shows the same part and view, for example
  the CX3170a XL lid render for the CX3171a. Reused renders are noted in the manual's
  inventory, and each reuse is listed in its pull request for review.
- Rack ears and pull handles are shared within each height: one 2U, one 3U and one 4U pair
  (`illustrations/common/hardware/{2U,3U,4U}{RackEars,PullHandles}.jpg`).
- 2U chassis have no motherboard tray, so they need no tray renders. 2U AIO renders may be
  supplied later; until then 2U manuals describe AIO installation in text.
- The CX3701 and CX3702 do not use motherboard standoffs. Of their successors (website concepts),
  the CX3150n (CX3701 "v2") uses no standoffs and the CX3180n (CX3702 "v2") uses standoffs.
- The CX3151i I/O-shield step uses the CX3151a or CX3151x render.
- The 5.25-inch bay filler blank is one part shared by every chassis with a 5.25-inch bay; all
  manuals use the same filler-blank page and renders (`illustrations/common/4u-bay-blank/`).
- Push-pull is not officially supported on the CX3150a (360 mm, six fans) or the CX3150i and
  CX3150x (240 mm, four fans), so no push-pull renders are requested for them.
- The CX4150e, CX4170e and CX4200e use the same 5.25-inch bay bracket; their bay-device steps
  share the CX4150e bracket renders (`illustrations/common/4u-bay-bracket/`).

## Published manuals: open items

| Model | Needed | Effect until supplied |
|---|---|---|
| CX3150i | Exploded view. Optional: bay-bracket-top HDD render (as 4k) with green E screws; 4k shows blue D, while the text specifies E (2026-11-05) | Exploded view omitted; the bracket-top HDD step shows blue screws |
| CX3150x | Exploded view. Optional: the cover render renamed (supplied as `_CX3150a_rendering.jpg` in the CX3150x folder) | Exploded view omitted |
| CX4150a | Exploded view | Exploded-view page omitted |
| CX4150e | Exploded view; push-pull renders (240 mm radiator, four fans) | Exploded view omitted; push-pull page is text only |
| CX4150i | Exploded view; push-pull renders (360 mm radiator, six fans) | Exploded view omitted; push-pull page is text only |
| CX4170a | Optional: external side/front dimension profiles; CRPS adapter steps, if the manual should cover CRPS | None (optional) |
| CX4170e | Push-pull renders (240 mm radiator, four fans) | Push-pull page is text only |
| CX4170i | Push-pull renders (360 mm radiator, six fans); radiator/drive-cage clearance renders (as CX4170a 4c1/4c2); a 5.25-inch device in the bay bracket | Push-pull and clearance pages are text only |
| CX4200a | Exploded view; radiator/drive-cage clearance renders | Exploded view omitted; clearance page is text only |
| CX4200e | Push-pull renders (240 mm radiator, four fans) | Push-pull page is text only |
| CX4200f | Push-pull renders (240 mm radiator, four fans) | Push-pull page is text only |
| CX4200i | Push-pull renders (360 mm radiator, six fans); radiator/drive-cage clearance renders; a 5.25-inch device in the bay bracket | Push-pull and clearance pages are text only |
| CX4712 | Exploded view; motherboard-tray removal and reinstallation renders (as CX4713 5a–5f; the tray is removable) | Exploded view and tray pages omitted |
| CX4713 | Exploded view; product render | Exploded view omitted |

## Cable management (not blocking V1)

Wanted for every rackmount manual, but no manual waits for them: until supplied, the
cable-management page is text only and refers to the cable-management bar on the top-view
clearance drawing. The CX3150a already has one (`CABLE_MANAGEMENT_BAR_HIGHLIGHT.jpg`, the bar
highlighted in green on the motherboard tray); the others need an equivalent view.

| Model | Needed |
|---|---|
| CX3150i, CX3150x | Cable-management bar highlighted on the tray (the CX3150a view may apply if the tray and view match; to confirm) |
| CX4150a, CX4150e, CX4150i | Cable-management bar highlighted on the tray |
| CX4170a, CX4170e, CX4170i | Cable-management bar highlighted on the tray |
| CX4200a, CX4200e, CX4200f, CX4200i | Cable-management bar highlighted on the tray |
| CX4712, CX4713 | Cable-management bar highlighted on the tray |

Every 3U and 2U manual built later joins this list unless its render set includes the view.

## 3U: not yet built

Several 3U variants have only a few renders. The column on the right lists the most likely
sibling to borrow shared steps from; each reuse is confirmed when that family is built.

| Model | Have | Needed | Possible source for shared steps |
|---|---|---|---|
| CX3151a | 59 | Exploded view | |
| CX3151i | 59 | Push-pull renders; exploded view | I/O shield from CX3151a/x (confirmed) |
| CX3152a | 6 | Installation steps | CX3152i |
| CX3152i | 40 | Push-pull renders; exploded view | |
| CX3170a | 11 | Installation steps; cover render | CX3170a XL |
| CX3170a XL | 48 | Push-pull renders; cover render | |
| CX3170i XL | 7 | Installation steps; cover render | CX3170a XL |
| CX3171a | 16 | Installation steps; cover render | CX3170a XL (lid confirmed as an example) |
| CX3171a XL, CX3171i XL | 17 / 9 | Installation steps; cover render | CX3170a XL |
| CX3172a | 8 | Installation steps; cover render | CX3172a XL |
| CX3172a XL | 37 | Push-pull renders; cover render | |
| CX3172i XL | 8 | Installation steps; cover render | CX3172a XL |
| CX3701 | 42 | AIO renders; front-panel render | No standoffs |
| CX3702 | 44 | Front-panel render | No standoffs |

## Concept models

The CX3150n, CX3180n, CX4250n and CX4280n are listed on the website as concepts ahead of
preorder. Their manuals are built once renders and specifications are available; none are
requested yet.

## 2U: not yet built

2U render sets are named and grouped differently; these are confirmed when each family is
built. No tray renders are needed (see above).

| Model | Have | Needed |
|---|---|---|
| CX2130a | 10 | SSD and GPU steps (and standoffs/I/O shield if not shown in the motherboard renders); clearance drawings; cover render; front-panel render |
| CX2130c | 18 | Standoffs/I/O shield, SSD and GPU steps; clearance drawings; cover render; front-panel render |
| CX2130x | none | Everything |
| CX2137a, CX2137b | 29 / 31 | To confirm (cover render and exploded view for CX2137a) |
| CX2151a, CX2151c, CX2151x | 25 / 31 / 23 | SSD step (CX2151a/c); clearance drawings and cover render (CX2151x); exploded views |
| CX2177a, CX2177c, CX2177x | 29 / 27 / 31 | To confirm; CX2177c also clearance drawings, cover and front-panel renders |
