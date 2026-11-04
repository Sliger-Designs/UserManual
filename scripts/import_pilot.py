#!/usr/bin/env python3
"""Rebuild draft chassis records from the catalog CSV exports; Python standard library only.

The CSV exports cover Sliger's whole catalog and stay private. Copy them into
`sources/original/` (ignored by Git) or pass --sources DIR. Generated product records keep
only the pilot models' rows, without internal catalog-status columns."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'compatibility': ('sources/original/compatibility-list.csv', 'SKU'),
    'bulk_create': ('sources/original/bulk-create.csv', 'Chassis Model'),
}
# Internal catalog-management columns, never copied into public product records.
INTERNAL_COLUMNS = {'On Website', '2BD Config Complete', '2BD Specs Complete', 'Amazon Listing'}
# Explicit mapping keeps source terminology and units visible. No guessed conversions.
FIELDS = {
    'product_type': 'Product Type', 'height_description': 'Height',
    'depth_in': 'Depth(in.)', 'width_in': 'Width(in.)', 'volume_l': 'Volume(L)',
    'material': 'Material', 'feature': 'Main feature', 'front_bays': 'Front Bay(s)',
    'ssd_2_5_max': 'Internal 2.5 SSD (Max)', 'hdd_3_5_max': 'Internal 3.5 HDD (Max)',
    'fans_max_description': 'Max Supported Fans',
    'front_fans_default': 'Front Fan Support(default)', 'front_fans_max': 'Front Fan Support(Max)',
    'mid_fans_default': 'Mid Chassis Fan Support', 'mid_fans_max': 'Mid-Chassis Fans(Max)',
    'exhaust_fans': 'Exhaust Fan Support', 'rear_fan_kit': 'KIT-REARFAN Support',
    'top_fan_kit': 'KIT-TOPFAN Support', 'air_cooler_height_max_mm': 'Max Air Cooler Height (mm)',
    'aio_2u': '2U AIO', 'aio_92': '92mm AIO', 'aio_120': '120mm AIO',
    'aio_140': '140mm AIO', 'aio_240': '240mm AIO', 'aio_280': '280mm AIO', 'aio_360': '360mm AIO',
    'psu_flex_atx': 'FlexATX PSU', 'psu_sfx_sfx_l': 'SFX/SFX-L PSU',
    'psu_crps': 'CRPS PSU', 'psu_atx': 'ATX PSU', 'motherboard_mini_itx': 'Mini-ITX MoBo',
    'motherboard_micro_atx': 'MicroATX MoBo', 'motherboard_atx': 'ATX MoBo(10.5" deep max)',
    'motherboard_eatx_13in': 'EATX MoBo(13" deep max)', 'riser_pcie_5': '5.0 Riser',
    'riser_bifurcation': 'Bifurcation Riser', 'pcie_slots': 'PCIe Slots',
    'gpu_height_max_mm': 'Max GPU Height (mm)',
    'gpu_length_baseline_mm': 'Max GPU Length Baseline(mm)',
    'gpu_length_fans_only_mm': 'Max GPU Length(Only Fans)(mm)',
    'gpu_length_fans_aio_mm': 'Max GPU Length(fans+AIO)(mm)',
    'gpu_length_max_cooling_mm': 'MAX GPU Length (Max cooling)',
}
NUMBERS = {'depth_in', 'width_in', 'volume_l', 'ssd_2_5_max', 'hdd_3_5_max',
           'air_cooler_height_max_mm', 'gpu_height_max_mm', 'gpu_length_baseline_mm',
           'gpu_length_fans_only_mm', 'gpu_length_fans_aio_mm', 'gpu_length_max_cooling_mm'}
ISSUES = {
    'CX3150a': [],
    'CX4150a': [],
    'CX4150e': [],
    'CX4150i': [],
    'CX4170a': ['P05', 'P06', 'P07', 'P08'],
    'CX4170e': [],
    'CX4170i': [],
    'CX4200a': [],
    'CX4200e': [],
    'CX4200f': [],
    'CX4200i': [],
    'S630': ['S600-02', 'S600-03'],
    'S640': ['S640-01', 'S600-02', 'S600-03'],
}

def read_source(path, key):
    with path.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames and len(reader.fieldnames) == len(set(reader.fieldnames))
        rows = []
        for index, row in enumerate(reader, 2):
            assert None not in row and all(v is not None for v in row.values()), (path, index)
            rows.append((index, row))
        return rows

def convert(field, raw):
    value = raw.strip()
    if not value:
        return None
    if value in ('TRUE', 'FALSE'):
        return value == 'TRUE'
    if field in NUMBERS:
        number = float(value)
        return int(number) if number.is_integer() else number
    return value

def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--sources', type=Path, default=ROOT / 'sources/original',
                        help='Folder holding compatibility-list.csv and bulk-create.csv (private)')
    args = parser.parse_args()
    data = {}
    supplemental = json.loads((ROOT / 'products/supplemental.json').read_text(encoding='utf-8'))
    overrides = json.loads((ROOT / 'products/overrides.json').read_text(encoding='utf-8'))
    manifest = {'sources': {}}
    for name, (relative, key) in SOURCES.items():
        path = args.sources / Path(relative).name
        if not path.is_file():
            raise SystemExit(f'Missing {path}: the catalog CSVs are private; pass --sources DIR')
        data[name] = read_source(path, key)
        manifest['sources'][name] = {
            'path': relative, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'row_reference': 'Logical CSV record number including header as record 1; not physical line number.',
        }
    for sku in ISSUES:
        matches = {}
        for name, (_, key) in SOURCES.items():
            found = [(n, r) for n, r in data[name] if r[key].strip() == sku]
            if not found and name == 'bulk_create' and sku in ('S630', 'S640'):
                continue  # These models are absent from the supplied bulk-create export.
            assert len(found) == 1, (sku, name, 'Expected exactly one source record')
            matches[name] = found[0]
        record_number, compat = matches['compatibility']
        facts = {}
        for field, column in FIELDS.items():
            facts[field] = {
                'value': convert(field, compat[column]),
                'source': {'id': 'compatibility', 'record': record_number, 'column': column},
                'raw': compat[column],
            }
        for field, evidence in supplemental.get(sku, {}).items():
            if field not in facts or facts[field]['value'] is None:
                facts[field] = evidence
        for field, decision in overrides.get(sku, {}).items():
            facts[field] = decision
        if compat['Product Type'].strip() == 'Rackmount':
            facts['hardware_bag_part_number'] = {
                'value': 'SBAG-HWKIT',
                'source': {'id': 'decision', 'date': '2026-10-27', 'record': 'products/shared/SBAG-HWKIT.json'},
                'note': 'All rackmount chassis share this screwbag as confirmed.'}
        record = {
            'schema_version': 1, 'sku': sku, 'status': 'draft',
            'release_ready': False, 'review_issues': ISSUES[sku],
            'authority': 'Explicit decisions in products/overrides.json take precedence, then populated compatibility entries; blanks mean unknown.',
            'facts': facts,
            'manual_copy_candidates': {
                column: {'text': raw.strip() or None,
                         'source': {'id': 'bulk_create', 'record': matches['bulk_create'][0], 'column': column},
                         'status': 'needs_review'}
                for column, raw in matches.get('bulk_create', (None, {}))[1].items()
                if column != 'Chassis Model'
            },
            'source_records': {
                name: {'record': number, 'fields': {column: value for column, value in row.items()
                                                    if column not in INTERNAL_COLUMNS}}
                for name, (number, row) in matches.items()
            },
        }
        if facts.get('aio_360_six_fan_push_pull_supported', {}).get('value') is False:
            candidate = record['manual_copy_candidates']['Max Length with AIO push-pull']
            candidate['status'] = 'excluded_unsupported_configuration'
            candidate['reason'] = 'Confirmed this configuration is officially unsupported.'
        (ROOT / 'products' / (sku + '.json')).write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n',
                                                        encoding='utf-8', newline='\n')
    (ROOT / 'sources' / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'Generated {len(ISSUES)} draft product records and source checksum manifest.')

if __name__ == '__main__':
    main()
