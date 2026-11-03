# English manual content

Manual content mirrors the illustration category folders. Use lowercase category names and preserve each chassis/SKU's original casing:

```text
content/en/
  desktop/
    S630/
    S640/
  2u/
  3u/
    CX3150a/
  4u/
    CX4170a/
  shared/
```

Edit a chassis's Markdown for wording. Its `manual.json` sets page titles, image captions, source files and page order. A page or step can use shared Markdown through `../../shared/...`; editing a shared file changes every manual that uses it.

Keep reusable procedures and reference wording in `shared/`. Category names also remain lowercase under future language folders. `scripts/manual_paths.py` maps each supported chassis to its category so builds do not depend on the old flat paths.

Stable page IDs can be retained across languages. Text and figure choices remain drafts pending technical review.
