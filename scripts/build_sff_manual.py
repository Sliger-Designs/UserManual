#!/usr/bin/env python3
"""Build SFF manuals from model content and selected publication images."""
import base64
import hashlib
import json
from pathlib import Path
from manual_paths import content_directory

import markdown
from jinja2 import Environment, StrictUndefined
from PIL import Image
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pymupdf
from manual_assets import LAYOUT_CHECK, build_directory, cover_photo, front_io_content, quantity_display, validate_template
from image_callouts import with_callouts
from manual_localization import Localizer

ROOT = Path(__file__).resolve().parents[1]


def image_data(path, expected_hash, alt):
    data = (ROOT / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected_hash, path
    mime = 'image/png' if Path(path).suffix == '.png' else 'image/jpeg'
    return {'src': f'data:{mime};base64,' + base64.b64encode(data).decode(), 'alt': alt}


def template_environment(product):
    """Jinja environment for manual Markdown and the page template."""
    env = Environment(undefined=StrictUndefined, autoescape=False)
    env.filters['zfill'] = lambda value, width: str(value).zfill(width)
    env.globals['fact'] = lambda key: product['facts'][key]['value']
    return env


def markdown_context(model):
    """Variables available to page Markdown (paired steps receive only `model`)."""
    return {'model': model, 'gpu_panel': 'panel 05' if model == 'S630' else 'panel 06',
            'storage_panel': 'panel 06'}


def markdown_environment(model, localizer=None):
    """(Jinja environment, variables) for rendering this model's Markdown placeholders."""
    product = json.loads((ROOT / f'products/{model}.json').read_text(encoding='utf-8'))
    env = template_environment(product)
    env.globals['t'] = (localizer or Localizer()).text
    return env, markdown_context(model)


def build(model, browser_path, public_preview=False, localizer=None, html_only=False, render_only=False):
    """Build one SFF manual. A localizer supplies translated text; html_only returns the
    normalized standalone HTML without layout checks or a PDF (used for editor templates);
    render_only returns the template output without a browser (used to record text)."""
    L = localizer or Localizer()
    english = L.is_source
    manual = json.loads((content_directory(model) / 'manual.json').read_text(encoding='utf-8'))
    product = json.loads((ROOT / f'products/{model}.json').read_text(encoding='utf-8'))
    common = json.loads((ROOT / 'illustrations/published/common/manifest.json').read_text(encoding='utf-8'))
    published = json.loads((ROOT / f'illustrations/published/{model}/manifest.json').read_text(encoding='utf-8'))
    assert manual['model'] == product['sku'] == model
    released = manual['release_ready']
    customer_facing = public_preview or released
    if public_preview:
        manual['revision'] = manual['publication_preview_revision']
        manual['status'] = 'User guide'
        for spec in manual['pages']:
            if spec['id'] == 'revision-history':
                spec['source'] = manual.get('publication_history_source', '../../shared/sff/publication-history.md')
    hardware = json.loads((content_directory(model) / 'hardware.json').read_text(encoding='utf-8'))
    if hardware.get('screwbag'):
        shared_hardware = json.loads((ROOT / hardware['screwbag']).read_text(encoding='utf-8'))
        assert model in shared_hardware['models']
        shared_by_letter = {entry['letter']: entry for entry in shared_hardware['items']}
        hardware['items'] = [{**shared_by_letter.get(entry['letter'], {}), **entry}
                             for entry in hardware['items']]
    hardware_page = next((number for number, spec in enumerate(manual['pages'], 1) if spec['layout'] == 'hardware-key'), None)
    for entry in hardware['items']:
        for field in ('name', 'description', 'color_label'):
            if entry.get(field):
                entry[field] = L.text(entry[field], f'hardware {entry["letter"]}: {field}', hardware_page)
        entry['quantity_display'] = quantity_display(entry.get('quantity'), L, f'hardware {entry["letter"]}: quantity', hardware_page)
    manual['language'] = L.language
    for field in ('cover_description', 'status', 'language_label'):
        manual[field] = L.text(manual[field], field, 1)
    def read_markdown(path, layout=None, page=None):
        return L.markdown(path.resolve().relative_to(ROOT).as_posix(), path.read_text(encoding='utf-8'), layout, page)
    hardware_by_letter = {entry['letter']: entry for entry in hardware['items']}
    def asset(name, caption, annotation_path=None, number=None):
        entry = common.get(name) or published[name]
        image = {**image_data(entry['path'], entry['sha256'], caption), 'caption': caption, 'key': name}
        if not annotation_path:
            return image
        annotation_file = content_directory(model) / annotation_path
        annotation = json.loads(annotation_file.read_text(encoding='utf-8'))
        fragments = []
        for fragment in annotation.get('image_fragments', []):
            source = common.get(fragment['asset_key']) or published[fragment['asset_key']]
            assert source['source_sha256'] == fragment['source_sha256'], 'Fragment source changed; review its location'
            assert 'no crop' in source['transformation'], 'Fragment coordinates require uncropped source'
            label = L.text(fragment['label'], 'diagram accessibility label', number)
            fragments.append({**fragment, 'label': label, **image_data(source['path'], source['sha256'], label),
                              'dimensions_px': source['dimensions_px']})
        return with_callouts(image, annotation_file, entry, fragments,
                             label=lambda text: L.text(text, 'diagram accessibility label', number))
    def caption(spec, name, number):
        text = spec.get('image_captions', {}).get(name)
        return L.text(text, 'image caption / alternative text', number) if text else name
    def figure_images(spec, number):
        names = spec.get('images', [])
        callouts = spec.get('hardware_callouts', [[] for _ in names])
        assert len(callouts) == len(names), 'One hardware callout group required per image'
        assert all(letter in hardware_by_letter for group in callouts for letter in group), 'Unknown hardware letter'
        return [{**asset(name, caption(spec, name, number),
                         spec.get('image_annotations', {}).get(name), number),
                 'hardware_items': [hardware_by_letter[letter] for letter in group]}
                for name, group in zip(names, callouts)]
    env = template_environment(product)
    env.globals['t'] = L.text
    pages = []
    for number, spec in enumerate(manual['pages'], 1):
        L.begin_page(number, spec)
        page = {**spec, 'images': []}
        if spec['layout'] != 'sff-cover':
            page['title'], page['section'] = L.text(spec['title'], 'title', number), L.text(spec['section'], 'section', number)
        sources = spec['source'] if isinstance(spec['source'], list) else [spec['source']]
        if spec['layout'] == 'sff-cover':
            sources = []  # The cover template shows no Markdown; it is not a translation source.
        parts = []
        rendered_sources = []
        for source in sources:
            text = read_markdown(content_directory(model) / source, spec['layout'], number)
            text = env.from_string(text).render(**markdown_context(model))
            parts.append(markdown.markdown(text, extensions=['tables', 'sane_lists']))
            rendered_sources.append(text)
        page['html'] = ''.join(f'<div class="reference-section">{part}</div>' for part in parts) if len(parts) > 1 else (parts[0] if parts else '')
        page['images'] = figure_images(spec, number)
        if spec['layout'] == 'front-io':
            page.update(front_io_content('\n'.join(rendered_sources), page['images'], spec.get('port_diagram_pending', False)))
        if spec['layout'] == 'sff-cover':
            page['images'] = [{**cover_photo(model), 'alt': model + ' ' + L.text('primary product photograph', 'cover image accessibility suffix', number)}]
        if spec['layout'] == 'hardware-key':
            page['hardware_items'] = [dict(entry,
                illustration=asset(entry['image'], entry['name'], number=number) if entry.get('image') else None,
                details=[asset(name, entry['name'], number=number) for name in entry.get('detail_images', [])])
                for entry in hardware['items']]
        if spec['layout'] == 'paired-procedure':
            page['steps'] = []
            for step in spec['steps']:
                source = read_markdown(content_directory(model) / step['source'], spec['layout'], number)
                rendered = env.from_string(source).render(model=model)
                page['steps'].append({**step, 'html': markdown.markdown(rendered, extensions=['tables', 'sane_lists']),
                    'images': figure_images(step, number)})
        if spec['layout'] == 'regulations':
            for name in ['RoHScompliant.png', 'REACHcompliant.png', 'ResponsibleMineralsInitive.png', 'MadeInUSA-reference.png']:
                entry = common['common/icons/' + name]
                page['images'].append(image_data(entry['path'], entry['sha256'], name))
        pages.append(page)
    css = (ROOT / 'templates/manual.css').read_text(encoding='utf-8') + '\n' + (ROOT / 'templates/sff-typography.css').read_text(encoding='utf-8')
    for marker, name in [('__TITILLIUM_REGULAR__', 'TitilliumWeb-Regular.ttf'), ('__TITILLIUM_BOLD__', 'TitilliumWeb-Bold.ttf')]:
        css = css.replace(marker, base64.b64encode((ROOT / 'templates/fonts' / name).read_bytes()).decode())
    logo = 'data:image/svg+xml;base64,' + base64.b64encode((ROOT / 'templates/brand/sliger-logo.svg').read_bytes()).decode()
    html = env.from_string((ROOT / 'templates/manual.html.j2').read_text(encoding='utf-8')).render(
        manual=manual, pages=pages, css=css, logo_src=logo, outer={})
    if render_only:
        return html
    edition =manual['revision'] if released else ('public-preview' if public_preview else 'prototype')
    if html_only:
        out = build_directory(model) / 'editor-template'
        out.mkdir(parents=True, exist_ok=True)
    elif not english:
        # Translations are built for review; approval and archiving remain separate steps.
        out = build_directory(model) / L.language
        out.mkdir(parents=True, exist_ok=True)
    elif released:
        out = ROOT / '_build/releases/chassis' / model / manual['revision']
        out.mkdir(parents=True, exist_ok=True)
    else:
        out = build_directory(model)
    html_path = out / f'{model}-{"editor-template" if html_only else L.language + "-" + edition}.html'
    pdf_path = html_path.with_suffix('.pdf')
    html_path.write_text(html, encoding='utf-8')
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_path, headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until='load')
        page.evaluate('document.fonts.ready')
        page.emulate_media(media='print')
        # SVG coordinates scale with the drawing; keep label type consistent in print.
        callout_typography = page.evaluate('''() => {
            const labels = [];
            for (const sheet of document.querySelectorAll('.sff')) {
                const probe = document.createElement('span');
                probe.style.cssText = 'position:absolute;visibility:hidden;font-size:var(--sff-type-small)';
                sheet.append(probe);
                const fontPx = parseFloat(getComputedStyle(probe).fontSize);
                probe.remove();
                for (const group of sheet.querySelectorAll('g[data-callout-number]')) {
                    const text = group.querySelector('text');
                    const circle = group.querySelector('circle');
                    const matrix = text.getScreenCTM();
                    const scale = Math.hypot(matrix.a, matrix.b);
                    if (!(scale > 0)) throw new Error('Invalid diagram label scale: ' + sheet.id);
                    text.style.fontSize = (fontPx / scale) + 'px';
                    text.style.fontWeight = '700';
                    circle.setAttribute('r', fontPx * 5 / 6 / scale);
                    const bounds = circle.getBoundingClientRect();
                    const frame = group.ownerSVGElement.getBoundingClientRect();
                    if (bounds.left < frame.left - 1 || bounds.top < frame.top - 1 ||
                        bounds.right > frame.right + 1 || bounds.bottom > frame.bottom + 1)
                        throw new Error('Diagram label clips its frame: ' + sheet.id);
                    labels.push({page:sheet.id, label:group.dataset.calloutNumber, font_size_pt:fontPx * .75, weight:700});
                }
            }
            return labels;
        }''')
        # Persist the same normalized SVG labels in standalone HTML and PDF.
        html = page.content()
        html_path.write_text(html, encoding='utf-8')
        if html_only:
            browser.close()
            return html
        # The translation editor runs this same check on its live preview.
        errors = page.evaluate(LAYOUT_CHECK)
        assert not errors, '\n'.join(error['message'] for error in errors)
        validate_template(page, model + ' ' + L.text('primary product photograph', 'cover image accessibility suffix', 1))
        expected_chips = sum(len(group) for spec in manual['pages']
                             for item in [spec, *spec.get('steps', [])]
                             for group in item.get('hardware_callouts', []))
        assert page.locator('.figure-hardware a').count() == expected_chips, 'Missing hardware color chips'
        page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
        browser.close()
    pdf = pymupdf.open(pdf_path)
    assert len(pdf) == len(pages)
    normalize = lambda value: ' '.join(value.split())
    for index, spec in enumerate(pages):
        assert normalize(spec['title']) in normalize(pdf[index].get_text()), (index, spec['title'])
        for step in spec.get('steps', []):
            for heading in BeautifulSoup(step['html'], 'html.parser').find_all(['h2', 'h3']):
                assert ' '.join(heading.get_text().split()) in ' '.join(pdf[index].get_text().split()), (spec['id'], 'Missing printed step', heading.get_text())
        assert pdf[index].rect.width == 792 and pdf[index].rect.height == 612
    text = '\n'.join(page.get_text() for page in pdf)
    assert '${pageNumberOnly}' not in text and '{{' not in text
    assert manual['revision'] in text
    if customer_facing:
        prohibited = ['working draft', 'technical review', 'canva', 'owner-confirmed',
                      'owner-approved', 'pending', 'before release', 'before publication',
                      'AI-assisted', 'prototype', 'source render', 'numbered overlay']
        assert not any(term.lower() in text.lower() for term in prohibited), 'Internal notes in public preview'
        assert not BeautifulSoup(html, 'html.parser').select('.asset-gap, .key-artwork-pending'), 'Placeholder in public preview'
    else:
        assert 'Technical review' in text
    if english:
        assert 'S630 and S640 use the same screw bag' in text
    # Shared reference wording is preserved instead of regenerated by AI.
    for spec, page in zip(pages, pdf):
        if not spec.get('reference_sections'):
            continue
        sources = spec['source'] if isinstance(spec['source'], list) else [spec['source']]
        for source in sources:
            expected = markdown.markdown(read_markdown(content_directory(model) / source), extensions=['tables'])
            for paragraph in BeautifulSoup(expected, 'html.parser').find_all('p'):
                assert normalize(paragraph.get_text()) in normalize(page.get_text()), source
    original_images = {name for item in manual['pages'] for group in [item, *item.get('steps', [])] for name in group.get('images', [])}
    fragment_sources = []
    for item in manual['pages']:
        for group in [item, *item.get('steps', [])]:
            for annotation_path in group.get('image_annotations', {}).values():
                annotation = json.loads((content_directory(model) / annotation_path).read_text(encoding='utf-8'))
                fragment_sources.extend(annotation.get('image_fragments', []))
    original_images.update(fragment['asset_key'] for fragment in fragment_sources)
    report = {'model': model, 'revision': manual['revision'], 'pages': len(pdf),
              'original_images': len(original_images), 'image_fragment_sources': fragment_sources,
              'diagram_label_typography': callout_typography,
              'release_ready': released, 'publication_preview': public_preview,
              'release_date': manual.get('release_date'),
              'real_model_renders_pending': any(step.get('illustration_pending') for spec in manual['pages'] for step in spec.get('steps', [])),
              'review_issues': product['review_issues'],
              'checks': ['model identity', 'publication image hashes', 'image loading',
                         'page titles and count', 'landscape Letter size', 'no page overflow or footer collisions',
                         'internal links', 'shared warranty/support/regulatory paragraphs preserved',
                         'diagonal cover banner, larger logo, website photo and vertical right language tab',
                         'two-column illustrated hardware key', 'instruction/reference pairing',
                         'separate dedicated motherboard and GPU/PCIe installation pages',
                         'per-image hardware color chips match declared model hardware references',
                         'customer copy contains no internal notes/placeholders' if customer_facing else 'draft labeling',
                         'no unresolved template expressions']}
    report['language'] = L.language
    if not english:
        report['release_ready'] = False
        report['translation_source'] = L.describe()
    output_prefix = model + ('' if english else '-' + L.language) + ('-' + edition if released or public_preview else '')
    (out / f'{output_prefix}-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    sheet = Image.new('RGB', (1605, ((len(pdf) + 2) // 3) * 425), '#d8dde0')
    for index, page in enumerate(pdf):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(.65, .65))
        im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        sheet.paste(im, ((index % 3) * 535 + 10, (index // 3) * 425 + 10))
    sheet.save(out / f'{output_prefix}-page-overview.jpg', quality=90)
    print(f'PASS: {model}: {len(pdf)} {edition} pages; HTML, PDF, overview and validation report in {out}')
    return {'pdf': pdf_path, 'html': html_path, 'overview': out / f'{output_prefix}-page-overview.jpg',
            'report': out / f'{output_prefix}-validation.json'}
