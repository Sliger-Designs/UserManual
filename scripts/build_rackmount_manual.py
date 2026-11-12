#!/usr/bin/env python3
"""Build rackmount manuals (CX3150a and the 4U models) from model content and selected publication images.

Same interface as build_sff_manual.build(); use manual_build.build() to pick the family."""
import base64
import hashlib
import json
import re

import markdown
from jinja2 import Environment, StrictUndefined
from playwright.sync_api import sync_playwright
import pymupdf
from PIL import Image

from image_callouts import with_callouts
from manual_assets import (LAYOUT_CHECK, build_directory, check_release, content_fingerprint, cover_photo, front_io_content,
                           number_pdf_pages, pending_image, retire_english_draft, split_contact, quantity_display, validate_template)
from manual_localization import Localizer
from manual_paths import MODEL_CATEGORIES, ROOT, content_directory, published_directory
from review_marks import borrowed_sources, colour, marked_data_uri


UNIT = re.compile(r'(?<=\d) (?=(?:mm|cm|inches|inch|kg|lbs?|W|Gbps|slots?)\b)|(?<=\d) (?=×)|(?<=×) (?=\d)')
NBSP = '\u00a0'


def keep_units_together(html):
    """Non-breaking spaces between numbers and their units (and around × between numbers) in
    text, so '270 mm' or '12 × 10.5' never splits across lines. Tags are left untouched."""
    return ''.join(part if part.startswith('<') else UNIT.sub(NBSP, part) for part in re.split(r'(<[^>]+>)', html))


_TRIM = {}


def content_inset(path, pad=0.03):
    """CSS object-view-box inset that crops a render's empty margins (near-white background),
    keeping a small pad, so procedure illustrations fill their frames. Published files are unchanged."""
    if path not in _TRIM:
        from PIL import Image, ImageChops
        with Image.open(path) as image:
            rgb = image.convert('RGB'); w, h = rgb.size
            box = ImageChops.difference(rgb, Image.new('RGB', rgb.size, (255, 255, 255))).point(lambda v: 255 if v > 18 else 0).getbbox()
        if not box:
            _TRIM[path] = ''
        else:
            l, t, r, b = box
            px, py = pad * w, pad * h
            l, t, r, b = max(0, l - px), max(0, t - py), min(w, r + px), min(h, b + py)
            _TRIM[path] = '' if (r - l) * (b - t) > 0.92 * w * h else (
                f'object-view-box: inset({100 * t / h:.2f}% {100 * (w - r) / w:.2f}% {100 * (h - b) / h:.2f}% {100 * l / w:.2f}%)')
    return _TRIM[path]


def top_view_drawing(item):
    """Top-view clearance drawings are tall: their notes go in a left column and the drawing's
    empty margins are cropped so it fills the rest of the page."""
    return item['layout'] == 'reference-drawing' and any('TOP VIEW' in name.upper() for name in item['images'] if not pending_image(name))


def load(model):
    manual = json.loads((content_directory(model) / 'manual.json').read_text(encoding='utf-8'))
    product = json.loads((ROOT / f'products/{model}.json').read_text(encoding='utf-8'))
    facts = {key: value['value'] for key, value in product['facts'].items()}
    hardware = json.loads((content_directory(model) / 'hardware.json').read_text(encoding='utf-8'))
    screwbag = json.loads((ROOT / hardware['screwbag']).read_text(encoding='utf-8'))
    # Additional packaged kits (e.g. CX-NAS-HWKIT) continue the lettering after the chassis items.
    extra = [item for path in hardware.get('additional_kits', [])
             for item in json.loads((ROOT / path).read_text(encoding='utf-8'))['items']]
    hardware['items'] = screwbag['items'] + hardware['items'] + extra
    return manual, product, facts, hardware, screwbag


def markdown_environment(model, localizer=None, state=None):
    """(Jinja environment, variables) for this model's Markdown. `hw()` and `ref()` route their
    English (hardware references, link labels, the word "page") through the localizer;
    `state['page']` is the page being rendered, recorded as each text's context."""
    L = localizer or Localizer()
    state = state if state is not None else {'page': None}
    manual, _, facts, hardware, _ = load(model)
    hardware_by_letter = {entry['letter']: entry for entry in hardware['items']}
    # Printed numbers: the cover is unnumbered, so a page's printed number is its 0-based index.
    printed_numbers = {entry['id']: index for index, entry in enumerate(manual['pages'])}

    def hw(letter):
        item = hardware_by_letter[letter]
        reference = L.text(item['reference'], f'hardware {letter}: reference in instructions', state['page'])
        return f'<a class="hw-ref" data-hardware="{letter}" data-hardware-color="{item.get("color", "neutral")}" href="#hardware-{letter}">{reference} <b>({letter})</b></a>'

    def ref(identifier, label):
        text = L.text(label, 'cross-reference link text', state['page'])
        word = L.text('page', 'cross-reference: word before the page number, as in "(page 8)"', state['page'])
        return f'<a href="#{identifier}">{text}</a> ({word} {printed_numbers[identifier]})'

    env = Environment(undefined=StrictUndefined, autoescape=False)
    env.filters['zfill'] = lambda value, width: str(value).zfill(width)
    env.globals.update(hw=hw, ref=ref, revision=manual['revision'], manual=manual, t=L.text)
    return env, {'facts': facts, 'outer': facts['outer_dimensions_mm']}


def build(model, browser_path, public_preview=False, localizer=None, html_only=False, render_only=False):
    """Build one rackmount manual. A localizer supplies translated text; html_only returns the
    standalone HTML without checks or a PDF (editor templates); render_only skips the browser
    entirely (used to record text)."""
    assert not public_preview, '--public-preview supports SFF manuals only'
    L = localizer or Localizer()
    english = L.is_source
    manual, product, facts, hardware, screwbag = load(model)
    assets = json.loads((published_directory(model) / 'manifest.json').read_text(encoding='utf-8'))
    assets.update(json.loads((published_directory('common') / 'manifest.json').read_text(encoding='utf-8')))
    if model == 'CX3150a':
        assert facts['aio_360_six_fan_push_pull_supported'] is False
    hardware_by_letter = {entry['letter']: entry for entry in hardware['items']}
    kit_letters = {item['letter'] for path in hardware.get('additional_kits', [])
                   for item in json.loads((ROOT / path).read_text(encoding='utf-8'))['items']}
    assert set(hardware_by_letter) == set('ABCDEFGHI') | kit_letters  # J (packing paper) removed 2026-11-04
    assert {item['letter']: int(item['quantity']) for item in screwbag['items']} == {
        'A': 45, 'B': 10, 'C': 20, 'D': 16, 'E': 10, 'F': 7}
    page_numbers = {entry['id']: index + 1 for index, entry in enumerate(manual['pages'])}
    hardware_page = page_numbers.get('hardware')
    for entry in hardware['items']:
        for field in ('name', 'description', 'color_label'):
            if entry.get(field):
                entry[field] = L.text(entry[field], f'hardware {entry["letter"]}: {field}', hardware_page)
        entry['quantity_display'] = quantity_display(entry.get('quantity'), L, f'hardware {entry["letter"]}: quantity', hardware_page)
    manual['language'] = L.language
    for field in ('cover_description', 'cover_description_detail', 'status', 'language_label'):
        if isinstance(manual.get(field), list):
            manual[field] = [L.text(line, field, 1) for line in manual[field]]
        elif field in manual:
            manual[field] = L.text(manual[field], field, 1)
    state = {'page': None}
    env, context = markdown_environment(model, L, state)
    env.globals['manual'] = manual

    def read_markdown(path, layout=None, page=None):
        return L.markdown(path.resolve().relative_to(ROOT).as_posix(), path.read_text(encoding='utf-8'), layout, page)

    compatibility_rules = json.loads((ROOT / 'products/shared/compatibility-rules.json').read_text(encoding='utf-8'))['rules']
    height_match = re.match(r'^(\d+)U\b', facts.get('height_description') or '')
    height_u = int(height_match.group(1)) if height_match else None
    applied_rules = []
    # English drafts mark renders borrowed from other models (review only; never in a release build).
    borrowed = borrowed_sources(model) if english and not manual.get('release_ready') else {}
    pages = []
    for number, item in enumerate(manual['pages'], 1):
        L.begin_page(number, item)
        state['page'] = number
        page = dict(item)
        if item['layout'] != 'cover':
            page['title'], page['section'] = L.text(item['title'], 'title', number), L.text(item['section'], 'section', number)
        sources = item['source'] if isinstance(item['source'], list) else [item['source']]
        if item['layout'] == 'cover':
            sources = []  # The cover template shows no Markdown; it is not a translation source.
        sections = []
        for source_index, source_path in enumerate(sources):
            source = read_markdown(content_directory(model) / source_path, item['layout'], number)
            if source_index == 0:
                for rule in compatibility_rules:
                    if height_u == rule['scope']['height_u'] and item['id'] in rule['scope']['page_ids']:
                        note = read_markdown(ROOT / rule['content'], item['layout'], number).strip()
                        source = note + '\n\n' + source
                        applied_rules.append({'id': rule['id'], 'page_id': item['id'], 'text': note})
            rendered = env.from_string(source).render(**context)
            sections.append(markdown.markdown(rendered, extensions=['tables', 'sane_lists']))
        sections, contact = split_contact(item['layout'], sections)
        page['contact_html'] = keep_units_together(contact)
        page['html'] = keep_units_together(''.join('<div class="reference-section">' + section + '</div>' for section in sections) if len(sections) > 1 else (sections[0] if sections else ''))
        page['images'] = []
        page['side_notes'] = top_view_drawing(item)
        for name in item['images']:
            if pending_image(name) is not None:
                text = L.text(pending_image(name), 'pending illustration placeholder', number)
                page['images'].append({'pending': text, 'key': name, 'src': '', 'alt': text, 'review': None, 'style': ''})
                continue
            asset = assets[name]
            path = ROOT / asset['path']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == asset['sha256']
            src = (marked_data_uri(path, colour(model, borrowed[name])) if name in borrowed else
                   ('data:image/png;base64,' if path.suffix == '.png' else 'data:image/jpeg;base64,') + base64.b64encode(path.read_bytes()).decode())
            page['images'].append({'src': src,
                                   'review': item.get('image_reviews', {}).get(name), 'key': name, 'alt': name.rsplit('.', 1)[0].replace('_', ' '),
                                   'style': content_inset(path) if (item['layout'] == 'procedure' or top_view_drawing(item)) and not item.get('keep_margins') else ''})
            if name in item.get('image_annotations', {}):
                page['images'][-1] = with_callouts(page['images'][-1], content_directory(model) / item['image_annotations'][name], asset,
                                                   label=lambda text: L.text(text, 'diagram accessibility label', number))
        if item['layout'] == 'cover':
            page['images'] = [{**cover_photo(model), 'alt': model + ' ' + L.text('primary product photograph', 'cover image accessibility suffix', number)}]
        if item['layout'] == 'front-io':
            page.update(front_io_content(rendered, page['images'], item.get('port_diagram_pending', False)))
        if item['layout'] == 'illustrated-cards':
            parts = re.split(r'^### (.+)$', rendered, flags=re.MULTILINE)
            card_images = page['images']
            assert len(parts) == 1 + 2 * len(card_images), item['id']
            page['html'] = markdown.markdown(parts[0])
            page['cards'] = [{'image': image,
                              'title': re.sub(r'^\d+\.\s*', '', parts[1 + i * 2]),
                              'description_html': markdown.markdown(parts[2 + i * 2]),
                              'html': markdown.markdown('### ' + parts[1 + i * 2] + '\n' + parts[2 + i * 2])}
                             for i, image in enumerate(card_images)]
        if item['layout'] == 'hardware-key':
            images_by_key = {image['key']: image for image in page['images']}
            letters = item.get('hardware_letters')
            page['hardware_items'] = [{**entry, 'illustration': images_by_key.get(entry['image']),
                                       'details': [images_by_key[name] for name in entry.get('detail_images', [])]}
                                      for entry in hardware['items'] if not letters or entry['letter'] in letters]
        if 'hardware_callouts' in item:
            assert len(item['hardware_callouts']) == len(page['images']), item['id']
            page['figure_keys'] = [[hardware_by_letter[letter] for letter in group] for group in item['hardware_callouts']]
        else:
            page['figure_keys'] = [[] for _ in page['images']]
        pages.append(page)
    state['page'] = None
    css = (ROOT / 'templates/manual.css').read_text(encoding='utf-8')
    for marker, filename in [('__TITILLIUM_REGULAR__', 'TitilliumWeb-Regular.ttf'), ('__TITILLIUM_BOLD__', 'TitilliumWeb-Bold.ttf')]:
        css = css.replace(marker, base64.b64encode((ROOT / 'templates/fonts' / filename).read_bytes()).decode())
    logo_src = 'data:image/svg+xml;base64,' + base64.b64encode((ROOT / 'templates/brand/sliger-logo.svg').read_bytes()).decode()
    html = env.from_string((ROOT / 'templates/manual.html.j2').read_text(encoding='utf-8')).render(
        manual=manual, pages=pages, css=css, logo_src=logo_src, outer=facts['outer_dimensions_mm'])
    if render_only or html_only:
        return html  # Rackmount pages need no browser normalization.

    # Approved English manuals build as release candidates (as SFF); archiving the PDF into
    # releases/ stays a separate, reviewed step. Translations are always review builds.
    released = english and bool(manual.get('release_ready'))
    fingerprint = content_fingerprint(html)
    if english:
        check_release(model, MODEL_CATEGORIES[model], manual['revision'], fingerprint)
    if released:
        assert not any(pending_image(name) is not None for item in manual['pages'] for name in item['images']), 'A release cannot contain pending-illustration placeholders'
        assert manual.get('release_date') and re.fullmatch(r'v\d+\.\d+', manual['revision']), 'A release needs release_date and a vN.N revision'
        out = ROOT / '_build/releases/chassis' / model / manual['revision']
        retire_english_draft(model)
    else:
        out = build_directory(model) / ('' if english else L.language)
    out.mkdir(parents=True, exist_ok=True)
    prefix = f'{model}-{L.language}-{manual["revision"] if released else "prototype"}'
    html_path, pdf_path = out / f'{prefix}.html', out / f'{prefix}.pdf'
    html_path.write_text(html, encoding='utf-8')
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_path, headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1200, 'height': 900}, device_scale_factor=1)
        page.goto(html_path.as_uri(), wait_until='load')
        page.evaluate('document.fonts.ready')
        page.emulate_media(media='print')
        errors = page.evaluate(LAYOUT_CHECK)
        assert not errors, '\n'.join(error['message'] for error in errors)
        validate_template(page, model + ' ' + L.text('primary product photograph', 'cover image accessibility suffix', 1))
        page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True, display_header_footer=False)
        browser.close()
    number_pdf_pages(pdf_path, pages, manual.get('display_name', model))

    pdf = pymupdf.open(pdf_path)
    assert len(pdf) == len(pages), (len(pdf), len(pages))
    text = '\n'.join(page.get_text() for page in pdf)
    normalize = lambda value: ' '.join(value.split())
    checks = manual.get('text_checks', {})
    assert checks.get('required'), 'manual.json must list the approved values the PDF has to show (text_checks.required)'
    for required in checks['required']:
        assert normalize(required) in normalize(text), ('Approved value missing from PDF', required)
    for forbidden in checks.get('forbidden', []):
        assert normalize(forbidden) not in normalize(text), ('Superseded or unsupported value in PDF', forbidden)
    assert 'SBAG-HWKIT' in text
    for i, spec in enumerate(pages):
        title = manual.get('display_name', model) if i == 0 else spec['title']
        assert normalize(title) in normalize(pdf[i].get_text()), (i, title)
        assert pdf[i].rect.width == 792 and pdf[i].rect.height == 612
    appendix_text = normalize(' '.join(pdf[index].get_text() for index, item in enumerate(pages) if item.get('reference_sections')))
    if english:  # The English reference wording is checked against the original manual.
        reference = pymupdf.open(ROOT / 'sources/original/cx3150a-reference.pdf')
        for index in (18, 19, 20):
            for block in reference[index].get_text('blocks'):
                words = block[4].strip()
                if words.isdigit() or words.startswith(('4.1 ', '4.2 ', '4.3 ', 'Website:', 'sliger.com')):
                    continue
                assert normalize(words) in appendix_text, ('Reference wording differs', index + 1, words)
        contact_labels = [re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', line).strip() for line in (ROOT / 'content/en/shared/support.md').read_text(encoding='utf-8').splitlines()
                          if line.startswith(('Website:', 'Support Email:', 'Phone Number:', 'Hours of Operation:'))]
        assert len(contact_labels) == 4, 'Expected four shared contact fields'
        for label in contact_labels:
            assert appendix_text.count(label) == 1, ('Contact wording differs', label)
    for rule in applied_rules:
        rule_text = normalize(rule['text'].replace('> ', '').replace('**', ''))
        assert rule_text in normalize(pdf[page_numbers[rule['page_id']] - 1].get_text()), rule['id']
    key_page = ' '.join(pdf[index].get_text() for index, item in enumerate(pages) if item['layout'] == 'hardware-key')
    for entry in hardware['items']:
        compact = lambda value: ''.join(value.split())  # names may wrap at hyphens, e.g. "217-735"
        assert compact(entry['name']) in compact(key_page), entry['letter']
    standoffs = [] if manual.get('no_standoffs') else ['(C)']  # e.g. CX3701/CX3702 boards mount without standoffs
    for identifier, expected in {
            'lid-removal': ['(A)'], 'tray-removal': ['(E)'], 'rack-ears': ['(F)', '(H)', '(I)'],
            'motherboard-preparation': standoffs, 'motherboard-installation': ['(A)'] + standoffs,
            'psu-installation': ['(A)'], 'gpu-installation': ['(A)', '(G)'],
            'ssd-installation': ['(B)', '5 mm long'], 'tray-installation': ['(E)']}.items():
        if identifier not in page_numbers:
            assert identifier in manual.get('omitted_pages', []), ('Required page missing', identifier)
            continue
        content = normalize(pdf[page_numbers[identifier] - 1].get_text())
        for required in expected:
            if english or required.startswith('('):
                assert required in content, (identifier, required)
    if model == 'CX4170a':
        gallery = next(item for item in manual['pages'] if item['id'] == 'drive-cage-layouts-1')
        gallery_text = normalize(pdf[page_numbers['drive-cage-layouts-1'] - 1].get_text())
        assert '8 × 7 mm' in gallery_text and '9 × 7 mm' in gallery_text
        assert len(gallery['images']) == 5
        assert not gallery.get('image_reviews')
        if english:
            assert 'Three HDDs + one SSD' in gallery_text
            assert 'Corrected eight-drive illustration pending' not in gallery_text
    assert all(letter in hardware_by_letter for item in manual['pages'] for group in item.get('hardware_callouts', []) for letter in group)
    assert len(next(item for item in manual['pages'] if item['id'] == 'regulations')['images']) == 4
    report = {'model': manual['model'], 'revision': manual['revision'], 'pages': len(pdf), 'language': L.language,
              'selected_images': len({name for item in manual['pages'] for name in item['images'] if pending_image(name) is None}),
              'pending_images': sorted({pending_image(name) for item in manual['pages'] for name in item['images'] if pending_image(name) is not None}),
              'checks': ['image hashes and loading', 'hardware A–I key and procedure references', 'internal links and generated page references', 'all four source regulatory images included', 'no page overflow or footer collisions', 'expected PDF page count and titles', 'landscape Letter page size', 'approved values present (text_checks.required)', 'superseded or unsupported values absent (text_checks.forbidden)',
                         'reference sections 4.1–4.3 body wording and repeated contact details match verbatim (whitespace normalized)' if english else 'translated text from ' + L.describe()],
              'applied_compatibility_rules': [{'id': rule['id'], 'page_id': rule['page_id']} for rule in applied_rules],
              'screwbag': screwbag['part_number'],
              'hardware_key': 'A–I; B corrected to red M3 × 0.5, 5 mm long',
              'missing_assets': manual.get('missing_assets', []),
              'review_marks': {name: source for name, source in sorted(borrowed.items())
                               if any(name in item['images'] for item in manual['pages'])},
              'release_ready': released, 'release_date': manual.get('release_date') if released else None,
              'content_fingerprint': fingerprint}
    report_prefix = model if english else f'{model}-{L.language}'
    (out / f'{report_prefix}-validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    sheet = Image.new('RGB', (3 * 535, ((len(pdf) + 2) // 3) * 425), '#d8dde0')
    for i, pg in enumerate(pdf):
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(.65, .65))
        sheet.paste(Image.frombytes('RGB', [pix.width, pix.height], pix.samples), ((i % 3) * 535 + 10, (i // 3) * 425 + 10))
    sheet.save(out / f'{report_prefix}-page-overview.jpg', quality=90)
    print(f'PASS: {model}: {len(pdf)} pages, {report["selected_images"]} images; HTML, PDF, overview, and validation report in {out}')
    return {'pdf': pdf_path, 'html': html_path, 'overview': out / f'{report_prefix}-page-overview.jpg',
            'report': out / f'{report_prefix}-validation.json'}
