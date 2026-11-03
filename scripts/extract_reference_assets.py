#!/usr/bin/env python3
"""Recover missing reference illustrations, with PDF provenance; no original is edited."""
import hashlib
import json
from pathlib import Path
import pymupdf
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'sources/original/cx3150a-reference.pdf'
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == json.loads((source.with_suffix('.metadata.json')).read_text())['sha256']
    pdf = pymupdf.open(source)
    jobs = [
        ('reference/CX3150a/exploded-numbered.png', 3, [94,126,724,352]),
        ('reference/CX3150a/side-profile.png', 4, [61,158,357,261]),
        ('reference/CX3150a/front-profile.png', 4, [364,158,703,261]),
        ('reference/CX3150a/front-ports-numbered.png', 6, [60,285,291,492]),
        ('common/hardware/slot-covers-reference.png', 5, 54),
        ('common/hardware/rack-ears-reference.png', 5, 55),
        ('common/hardware/pull-handles-reference.png', 5, 56),
        ('common/icons/MadeInUSA-reference.png', 21, 141),
    ]
    extracted=[]
    for key, page_number, extraction in jobs:
        target = ROOT / 'illustrations' / key
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(extraction, list):
            pix=pdf[page_number-1].get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(extraction),alpha=False)
            method={'clip_pt':extraction,'render_scale':3}
        else:
            record=next(x for x in pdf[page_number-1].get_images(full=True) if x[0]==extraction)
            pix=pymupdf.Pixmap(pdf,extraction)
            if record[1]:pix=pymupdf.Pixmap(pix,pymupdf.Pixmap(pdf,record[1]))
            method={'image_xref':extraction,'soft_mask_xref':record[1]}
        pix.save(target)
        extracted.append({'id':'reference-'+hashlib.sha256(key.encode()).hexdigest()[:12],
            'asset_key':key,'original_filename':target.name,'local_path':target.relative_to(ROOT).as_posix(),
            'width_px':pix.width,'height_px':pix.height,'size_bytes':target.stat().st_size,
            'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'selection_status':'candidate',
            'reference':{'path':source.relative_to(ROOT).as_posix(),'sha256':digest,'page':page_number,**method}})
    (ROOT/'illustrations/reference.inventory.json').write_text(json.dumps({'schema_version':1,'items':extracted},indent=2)+'\n')
    print('Recovered eight reference illustrations with page and extraction provenance.')
if __name__=='__main__': main()
