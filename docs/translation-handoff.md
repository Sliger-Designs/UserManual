# Translating the ${manuals} manuals

<!-- Template: the translation editor shows this as its instructions, and
     scripts/translation_package.py export saves a copy as the package README.
     ${...} values are filled in per package. Model-family guidance comes from
     docs/translation-notes/<family>.md. -->

Translate in the Sliger translation editor (open a manual on the Sliger manuals
site and choose a language under **Translate**). It shows each page of the manuals as sentence-sized
items beside a live preview of the real page. Text shared by several manuals
appears once and only needs translating once.

## How to work

1. Open the editor, choose your language and fill in the details under
   **Start here**: language name, translator, reviewer.
2. Work through the pages on the left. Type each translation under its English
   text; the preview on the right shows the page as you type. A "fit" marker
   means the text is too long for its page: shorten it until the marker goes.
3. Your work is saved automatically, but only in this browser on this computer.
   Click **Download translation file** regularly as a backup. **Open file…**
   continues from that file on another computer or browser.
4. When the translation is finished and reviewed, download the translation file
   and send it to Sliger (**Send to Sliger** explains how). It is one small file
   that holds all your translations and details.
5. **Create PDF** prints a manual from your translation for your own review.

## Preserve while translating

The editor highlights text that must stay exactly as written and marks the item
red if it changes. You may move highlighted parts within the sentence.

- Placeholders such as `{{ fact('gpu_length_baseline_mm') }}` insert approved
  measurements; model-specific passages are marked with the model they apply to.
  Translate every model's version.
- Keep HTML tags such as `<strong>` and `<p class="info-note" role="note">`;
  translate the text inside them.
- Keep hardware reference letters ${hardware_letters}, model names, part numbers,
  technical identifiers (${terms}), numbers, units and screw specifications,
  revision ${version} and dates unchanged. Do not convert measurements or change
  decimal separators.
- Keep contact details, email addresses, links and brand names unchanged.
- Translate color names such as "Yellow" and "Green-marked"; they appear as
  their own items.
${family_notes}
Text baked into product artwork, logos and regulatory badges cannot be edited
here. Note anything that needs a localized illustration, terminology questions
and text intentionally left in English under **Notes for Sliger**.

## Review checklist

- [ ] Every page of every manual is translated, including warranty, support and
      regulatory pages.
- [ ] Every model's version of a model-specific passage is translated.
- [ ] No page shows a "fit" marker.
- [ ] Hardware letters, quantities, measurements and product names are unchanged.
- [ ] A native-language reviewer has checked terminology and technical meaning.
- [ ] Questions and illustration requests are in **Notes for Sliger**.
