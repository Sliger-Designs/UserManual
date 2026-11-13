# Translating a Sliger manual

Anyone can help translate the Sliger chassis manuals. You need a web browser and nothing
else: no GitHub account is needed to translate, no software to install, and no files from
this repository.

**Translation site:** <https://sliger-designs.github.io/UserManual/>

## Start

1. Open the translation site and find the manual (or group of manuals) you want to
   translate.
2. Choose your language under **Translate**. The translation editor opens with its full
   instructions under **Start here**.
3. Enter the language name, your name as translator, and the reviewer's name.

## Translate

- The editor shows each page as sentence-sized items beside a live preview of the printed
  page. Type each translation under its English text.
- Text shared by several manuals appears once. When you open another manual in the same
  browser and language, the text you have already translated is filled in.
- A "fit" marker means the text is too long for its page: shorten it until the marker
  goes.
- Highlighted text must stay exactly as written: placeholders, HTML tags, hardware
  reference letters, model names, part numbers, numbers, units, dates, links and contact
  details. The editor marks an item red if one of these changes. Translate color names
  such as "Yellow".
- Your work is saved automatically, but only in that browser. Click **Download translation
  file** regularly as a backup; **Open file…** continues from it on another computer.
- **Create PDF** prints a manual from your translation for your own review.
- Put questions, terminology choices and text intentionally left in English under
  **Notes for Sliger**.

## Send the translation

When the translation is finished and a native-language reviewer has checked it:

1. Click **Download translation file**. It is one small file ending in
   `-translation.json`. Do not edit it.
2. Return it either way:
   - **On GitHub:** open a
     [Return a translation](https://github.com/Sliger-Designs/UserManual/issues/new?template=translation-return.yml)
     issue and drag the file into it (needs a free GitHub account).
   - **By email:** click **Send to Sliger** in the editor, which opens an email with the
     details filled in; attach the file.

Sliger reviews the translation, imports it, and builds the translated PDFs. On GitHub, the
pull request with the PDFs is linked from your issue.

## Updates

Returned translations are kept in a translation memory for each language. When a manual
changes, only the new or changed text needs translating; the editor fills in the rest.

Maintainers: the export, import and build commands are in the
[README](../README.md#translations), [translation-packages/README.md](../translation-packages/README.md)
and [translations/README.md](../translations/README.md).
