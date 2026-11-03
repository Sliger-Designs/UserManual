# Publishing template

`manual.html.j2` and `manual.css` create the prototype's landscape Letter document. Content is maintained in Markdown; the assembly manifest selects pages and images. Shared styling controls typography, red rules, language tag, figure numbering, headers, and footers. Product facts remain in `products/`.

The browser HTML is self-contained; the same HTML is printed to PDF by Chromium through Playwright. No website hosting or deployment is required. Page boundaries are explicit and checked for overflow. Any language requiring more room needs layout adjustment or additional pages before release.

Hardware badges use each item's shared color name: A yellow, B red, C teal (drawing highlight only; actual standoffs are black and unpatched), D blue, E green, F pink. Diagram badges, inline references, and hardware-key letters use the same palette; yellow, teal, and pink use dark lettering. Non-color-coded accessories use neutral gray. Letters and color names remain visible alongside the color.

## S630 / S640 typography

`sff-typography.css` defines the shared type roles for both SFF manuals. The SFF
builder loads it after the base layout CSS, so layout-specific rules do not create
different body sizes. Heading text uses Titillium Web; inline emphasis inherits
the body font. Regular and bold use weights 400 and 700.

| Role | Size | Weight |
|---|---|---|
| Page title | 25 pt | 700 |
| Subsection heading | 12 pt | 700 |
| Body, tables and contents entries | 10 pt | 400; headers/emphasis 700 |
| Hardware item name and quantity | 10 pt | 700 |
| Hardware description, notes, captions and chip text | 9 pt | 400; emphasis/letters 700 |
| Diagram callout number | 9 pt | 700 |
| Section label / footer metadata | 8 pt | 700 / 400 |
| Page number | 12 pt | 700 |
| Cover title / subtitle | 43 pt / 15 pt | 700 / 400 |

Body leading is 1.35; secondary text uses 1.3 and captions use 1.25. During the SFF
build, diagram text and circles are normalized to physical print size after image
layout. The same attributes are saved into standalone HTML and PDF. Image source
coordinates and callout positions remain unchanged. Build reports record each
diagram label's printed size and weight.

## Larger SFF procedure illustrations

An SFF page can set `"illustration_size": "large"` in its manual manifest to
give a single illustration 65% of the page width, or a two-view row a 4.05-inch
image height. Use source-hash-bound framing annotations to remove blank margins
without changing the bitmap. Keep hardware chips and captions below each image.

Supporting SFF notes can use `<p class="info-note" role="note">…</p>` in their
Markdown source. A small gray outlined information icon sits in the left margin;
the note keeps its surrounding type size. Reserve this for explanatory notes,
such as compatibility limits and hardware details, rather than assembly steps.
