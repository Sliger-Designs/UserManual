"""Asset helpers shared by both manual families."""
import base64
import hashlib
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


def build_directory(model):
    directory = ROOT / '_build' / 'unpublished' / 'chassis' / model
    directory.mkdir(parents=True, exist_ok=True)
    guide = ROOT / '_build/README.md'
    if not guide.exists():
        guide.write_text(
            '# Build outputs\n\n'
            '- `releases/chassis/<model>/<revision>/`: builds of released manuals.\n'
            '- `unpublished/chassis/<model>/`: drafts, translated builds (`<language>/`) and previews.\n'
            '- `translation-editor/<package>/`: browser translation editors.\n\n'
            'Build outputs are local and excluded from Git. See the repository README for details.\n',
            encoding='utf-8')
    return directory


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
