# Translations

One folder per language holds that language's translation memory, the stored form
of every approved-for-review translation:

- `<lang>/memory.json`: English text → translation. Keys are whole labels (titles,
  captions, hardware names) or single Markdown segments (a heading, step, table cell,
  paragraph or note) as split by `scripts/translation_segments.py`, the same units the
  browser editor shows. Each entry records the package it came from, the import date,
  and the translator and reviewer.
- `<lang>/imports/<package>.json`: what each import brought in, with the returned
  `job.json` (translator notes) and any Markdown that could not be imported.

One memory serves every manual and every version. Text shared between manuals
(warranty, support, regulations, shared procedures) is translated once. When English
changes, only new or edited segments are missing; everything else still applies.

## Workflow

```bash
# 1. Import a returned package (editor ZIP or edited package folder); it is validated first.
python3 scripts/translation_memory.py import /path/to/returned.zip

# 2. See which manuals the language can build.
python3 scripts/translation_memory.py status de --models S630 S640

# 3. Build review PDFs (stops on missing text; --allow-incomplete makes an English-filled draft).
python3 scripts/build_manual.py --model S630 --language de

# 4. For the next version or another manual, give the translator a pre-filled editor:
#    only new text is empty; reused translations are marked "From translation memory".
python3 scripts/translation_editor.py translation-packages/<package> --language de
```

Importing replaces an entry when the returned translation differs, so review the
`memory.json` diff before committing; Git keeps the history. Builds check every
entry's protected text (placeholders, hardware letters, numbers, model names) against
its English and report invalid entries instead of printing them.

Entries whose English no longer appears in any manual are harmless and can be kept for
reuse. Built translations are never marked released: approve each language's PDFs
and archive them under `releases/<lang>/` as a separate step.
