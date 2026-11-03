# S630 and S640 v1.0 translation handoff

This package contains the text used by the approved English S630 and S640 v1.0
manuals. Translate both together: shared procedures need translation only once.
The English PDFs in `reference/en/desktop/` show the images and page layout.
`page-map.json` maps each manual's 23 pages to the Markdown files used on it.
Some pages use multiple files; filenames do not correspond one-to-one to pages.

## What to return

Return the complete package folder or ZIP, keeping its filenames and folders.
Edit only the files inside `translation/`:

1. Set `target_language` (for example `de`), `target_language_name` (the language's
   own name), and translator/reviewer details in `translation/job.json`.
2. Translate the Markdown in `translation/content/desktop/S630/`,
   `translation/content/desktop/S640/` and `translation/content/shared/`.
3. In `translation/strings.json`, fill in each `translation` value. These are
   page titles, section headings, captions, hardware names/descriptions, color
   labels, cover/footer text, and accessibility labels outside Markdown. Each
   unique English string appears once; `contexts` explains every place it is
   used. Leave `source`, IDs and `contexts` unchanged. Use valid UTF-8 JSON;
   escape quotes inside values as `\"` and use `\n` for line breaks.
4. Put terminology questions, intentional unchanged text and any layout concerns
   in `translation/job.json` under `notes`.

`source/` is the read-only English baseline for comparison. `reference/`,
`manifest.json`, `page-map.json`, `terminology.md` and this README are context,
not translation deliverables to edit. No illustration-coordinate JSON, unused
render-reference Markdown or internal draft history is included for translation.

## Preserve while translating

- Keep filenames, folder names, page order, Markdown headings, lists and tables.
  Translate heading text and table cells, not their Markdown structure.
  Keep the two trailing spaces used for line breaks in the contact details.
- Keep Jinja expressions such as `{{ fact('gpu_length_baseline_mm') }}` exactly.
  They insert approved technical values during the build.
- Keep `{% if model == 'S630' %}`, `{% else %}` and `{% endif %}` exactly, in
  order. Translate both branches; they provide the model-specific bracket text.
- Keep HTML tags and attributes, including `<p class="info-note" role="note">`
  and `<strong>`. Translate their enclosed prose.
- Keep hardware reference letters A–H, model names, part numbers, technical
  identifiers (ATX, SFX, SFX-L, EATX, PCIe, USB, M3, 6-32), numerical values,
  units/screw specifications, revision v1.0 and dates unchanged. Do not convert
  measurements or change decimal separators in this handoff.
- Keep contact details, email addresses, links and brand names unchanged.
- Do not translate internal color keys or asset paths in `contexts`. Translate
  display values such as “Yellow” and “Green-marked” in `translation` instead.
- The two models use different PCIe retention screws: S630 uses blue E and S640
  uses yellow A. Preserve those differences and the hardware identifiers.

The shared C standoff uses a teal drawing highlight but the physical hardware is
black. Use the English PDF and `terminology.md` for context. Text already baked
into product artwork, logos and regulatory badges is not editable text in this
package; flag anything that requires a localized illustration in the job notes.

## Review checklist

- [ ] Both manuals' model-specific files are translated.
- [ ] All shared files are translated once, including warranty/support/regulations.
- [ ] Both branches of model-dependent passages are translated.
- [ ] Every `translation` value in `strings.json` is filled in. If an English
      technical term stays unchanged, copy it explicitly into the translation.
- [ ] Hardware letters, quantities, measurements and product names are unchanged.
- [ ] A native-language reviewer has checked terminology and technical meaning.
- [ ] Unclear source wording and illustration-localization requests are noted.

## Maintainer validation and integration

From the repository, run:

```bash
python3 scripts/translation_package.py validate /path/to/returned-package --complete
```

Without `--complete`, the checker accepts a fresh, untranslated package and
reports how many items need translation/review. It checks the English baseline,
file inventory, label IDs, source/context fields, placeholders, HTML, Markdown
structure, hardware references, URLs and numeric values. Identical Markdown is
flagged for human review rather than rejected: some short technical content may
legitimately remain unchanged. Passing validation does not establish translation
accuracy or PDF layout quality.

The manifest records the English source commit, file hashes and exact reference
PDF hashes so the translation can be checked against the version sent out. The
package is pinned to v1.0; later English changes need separate reconciliation.

Returned translations do not automatically replace English content or create a
released manual. Language-aware build/import support still needs to be added.
After integration, the intended content paths are
`content/<target_language>/desktop/<model>/` and
`content/<target_language>/shared/`. Titles and labels must also be wired into
the localized build. Build both manuals, review every page for text expansion,
fonts, clipping, callouts and links, and approve each language before saving
release PDFs under `releases/<target_language>/desktop/<model>/v1.0/`.
