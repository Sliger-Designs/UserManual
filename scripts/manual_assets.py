"""Asset helpers shared by both manual families."""
import base64
import hashlib
from html import unescape
import json
import re
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parents[1]
# Shared by both builds and the translation editor's live preview; returns [{page, message}].
LAYOUT_CHECK = (ROOT / 'scripts/manual_layout_check.js').read_text(encoding='utf-8')


def quantity_display(quantity, localizer, use, page):
    """'20' -> '20 ×'; worded quantities such as '1 pair' are translatable text."""
    if not quantity:
        return quantity
    return localizer.text(quantity, use, page) if re.search('[A-Za-z]', quantity) else quantity + ' ×'


BUILD_GUIDE = ('# Build outputs\n\n'
               '- `releases/chassis/<model>/<revision>/`: builds of released (reviewed and approved) manuals.\n'
               '- `unpublished/chassis/<model>/`: English drafts still awaiting review, and translated builds\n'
               '  (`<language>/`). Building a released manual removes its leftover English draft here,\n'
               '  so the models listed under `unpublished/chassis/` with an English PDF are the ones still to review.\n'
               '- `translation-editor/<package>/`: browser translation editors (`templates/<model>/`: their page templates).\n\n'
               'Build outputs are local and excluded from Git. See the repository README for details.\n')


def build_directory(model, draft=True):
    directory = ROOT / '_build' / 'unpublished' / 'chassis' / model
    if draft:
        directory.mkdir(parents=True, exist_ok=True)
    guide = ROOT / '_build/README.md'
    guide.parent.mkdir(parents=True, exist_ok=True)
    if not guide.exists() or guide.read_text(encoding='utf-8') != BUILD_GUIDE:
        guide.write_text(BUILD_GUIDE, encoding='utf-8')
    return directory


def retire_english_draft(model):
    """A released manual no longer needs review: remove its leftover English draft outputs
    from _build/unpublished (translated builds in language subfolders stay)."""
    directory = build_directory(model, draft=False)
    if not directory.is_dir():
        return
    for path in directory.iterdir():
        if path.is_file():
            path.unlink()
    if not any(directory.iterdir()):
        directory.rmdir()


def content_fingerprint(html):
    """Hash of what a reader sees in a built manual: its visible text and every embedded image.
    Styling (CSS, fonts, scripts) is left out, so a spacing or layout tweak is not a content change."""
    html = re.sub(r'<(style|script)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    data_uri = r'data:image/[^"\'()\s]+'
    images = [hashlib.sha256(uri.encode()).hexdigest() for uri in re.findall(data_uri, html)]
    text = re.sub(r'<[^>]+>', ' ', re.sub(data_uri, '', html))
    text = ' '.join(unescape(text).split())
    return hashlib.sha256(json.dumps({'text': text, 'images': images}).encode()).hexdigest()


def release_record_path(model, category, revision, language='en'):
    return ROOT / 'releases' / language / category / model / revision / f'{model}-{language}-{revision}.json'


def released_versions(model, category, language='en'):
    """Archived release records of a manual, oldest first."""
    folder = ROOT / 'releases' / language / category / model
    records = [json.loads(path.read_text(encoding='utf-8')) for path in folder.glob(f'*/{model}-{language}-*.json')]
    return sorted(records, key=lambda record: [int(part) for part in record['revision'].lstrip('v').split('.')])


def check_release(model, category, revision, fingerprint):
    """Fail when a released revision's content changed: a released PDF must stay reproducible.
    Editing a released manual means drafting a new revision (see releases/README.md)."""
    path = release_record_path(model, category, revision)
    if path.is_file():
        record = json.loads(path.read_text(encoding='utf-8'))
        assert record['content_fingerprint'] == fingerprint, (
            f'{model} {revision} is released, but its content has changed since the release. '
            f'Set "revision" to the next version (e.g. v1.1) and "release_ready" to false while drafting it, '
            f'or undo the change. See releases/README.md.')


def cover_photo(model):
    entry = json.loads((ROOT / 'illustrations/published/covers/manifest.json').read_text(encoding='utf-8'))[model]
    data = (ROOT / entry['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], entry['path']
    return {'src': 'data:image/jpeg;base64,' + base64.b64encode(data).decode(),
            'alt': model + ' primary product photograph', 'key': 'website-cover-photo'}


def front_io_content(rendered, images, location_pending=False):
    """Use one connector drawing/numbered legend convention for every family."""
    parts = re.split(r'^### (.+)$', rendered, flags=re.MULTILINE)
    connectors = images if location_pending else images[1:]
    assert len(connectors) == 3 and len(parts) == 7, 'Front I/O requires three numbered connector references'
    return {
        'html': markdown.markdown(parts[0]),
        'cards': [{'image': image, 'title': re.sub(r'^\d+\.\s*', '', parts[1 + index * 2]),
                   'description_html': markdown.markdown(parts[2 + index * 2]),
                   'html': markdown.markdown('### ' + parts[1 + index * 2] + '\n' + parts[2 + index * 2])}
                  for index, image in enumerate(connectors)]}


def validate_template(page, cover_alt='primary product photograph'):
    """Check the shared visual conventions requested for all chassis manuals.
    `cover_alt` is the (localized) ending of the website cover photograph's alt text."""
    errors = page.evaluate('''(coverAlt) => {
        const errors = [];
        const cover = document.querySelector('.cover');
        if (cover) {
            const banner = cover.querySelector('.cover-banner');
            const logo = cover.querySelector('.brand-logo');
            const tag = cover.querySelector('.language-tag');
            const photo = cover.querySelector('.cover-image');
            if (!banner || getComputedStyle(banner).clipPath === 'none') errors.push('Missing diagonal cover banner');
            if (logo.getBoundingClientRect().width < 330) errors.push('Cover logo too small');
            if (getComputedStyle(tag).writingMode !== 'vertical-rl') errors.push('Language tag is not vertical');
            if (Math.abs(tag.getBoundingClientRect().right - cover.getBoundingClientRect().right) > 1) errors.push('Language tag is not on right edge');
            if (!photo || !photo.alt.endsWith(coverAlt)) errors.push('Cover must use website photograph');
        }
        const key = document.querySelector('#hardware .key-grid');
        if (!key || getComputedStyle(key).gridTemplateColumns.split(' ').length !== 2) errors.push('Hardware kit must use two-column illustrated key');
        const motherboard = document.querySelector('.page#motherboard-installation');
        const gpu = document.querySelector('.page#gpu-installation');
        if (!motherboard || !gpu || motherboard === gpu) errors.push('Motherboard and GPU/PCIe installation require separate dedicated pages');
        for (const step of document.querySelectorAll('.paired-step'))
            if (!step.querySelector('article') || !step.querySelector('.paired-images')) errors.push('Unpaired instruction/reference');
        const io = document.querySelector('.page#front-ports, .page#ports');
        if (!io || !io.classList.contains('front-io') || io.querySelectorAll('.io-connector img').length !== 3 || io.querySelectorAll('.io-legend tbody tr').length !== 3)
            errors.push('Front I/O requires location image, three connector drawings and numbered legend');
        return errors;
    }''', cover_alt)
    assert not errors, '\n'.join(errors)


def split_contact(layout, sections):
    """Warranty & support: the contact lines after the `---` rule in shared/support.md leave the
    columns and sit centered at the bottom of the page. Returns (sections, contact_html)."""
    if layout != 'reference-columns' or not sections or '<hr />' not in sections[-1]:
        return sections, ''
    last, contact = sections[-1].split('<hr />', 1)
    return sections[:-1] + [last], contact.strip()


def number_pdf_pages(pdf_path, pages, cover_label):
    """The cover is unnumbered and "In this guide" is page 1. Give the PDF matching page labels
    so a viewer's page box agrees with the printed numbers (and with "(page N)" references)."""
    import pymupdf
    assert pages[0]['layout'] in ('cover', 'sff-cover'), 'The first page must be the cover'
    pdf = pymupdf.open(pdf_path)
    pdf.set_page_labels([{'startpage': 0, 'prefix': cover_label, 'style': '', 'firstpagenum': 1},
                         {'startpage': 1, 'prefix': '', 'style': 'D', 'firstpagenum': 1}])
    pdf.save(pdf_path, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    pdf.close()
