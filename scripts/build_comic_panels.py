"""Deterministic panel pipeline. Each work defines its own source rectangles.

Run from anywhere. --verify checks outputs without rebuilding them.
Sources are never modified; lossless PNGs are the pixel comparison baseline.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / '_data/comic_panel_specs.json'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_crop(source, item):
    if 'pieces' not in item:
        return source.crop(item['box'])
    image = Image.new('RGB', tuple(item['canvas_size']), 'white')
    used = Image.new('1', image.size)
    for piece in item['pieces']:
        crop = source.crop(piece['box'])
        x,y = piece['at']
        assert 0 <= x <= image.width-crop.width and 0 <= y <= image.height-crop.height
        rect = (x,y,x+crop.width,y+crop.height)
        assert used.crop(rect).getbbox() is None, 'Overlapping output pieces'
        image.paste(crop, (x,y))
        ImageDraw.Draw(used).rectangle((x,y,rect[2]-1,rect[3]-1),fill=1)
    return image

def edited(crop, item):
    image = crop.copy()
    for edit in item.get('edits', []):
        box = edit['box']
        draw = ImageDraw.Draw(image)
        draw.rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=edit['color'])
        if edit.get('text'):
            font = ImageFont.truetype(edit.get('font', 'C:/Windows/Fonts/arialbd.ttf'), edit.get('font_size', 30))
            draw.text(((box[0]+box[2])/2, (box[1]+box[3])/2), edit['text'], font=font, anchor='mm', fill='white')
    return image

def verify_crop(source, crop, item):
    box = item['box']
    expected = source_crop(source, item)
    assert crop.size == expected.size
    diff = ImageChops.difference(crop, expected)
    for edit in item.get('edits', []):
        x0,y0,x1,y1 = edit['box']
        assert 0 <= x0 < x1 <= crop.width and 0 <= y0 < y1 <= crop.height
        ImageDraw.Draw(diff).rectangle((x0,y0,x1-1,y1-1), fill=(0,0,0))
    assert diff.getbbox() is None, 'Pixels changed outside declared edit region'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--only', help='Build or verify one work; retain all other manifest entries')
    args = parser.parse_args()
    specs = json.loads(SPEC.read_text(encoding='utf-8'))
    manifest_path = ROOT / '_data/comic_panels.json'
    saved = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    manifest, report = (dict(saved) if args.only else {}), []
    if args.only:
        specs = [w for w in specs if w['id'] == args.only]
        assert len(specs) == 1, 'Missing or duplicate work specification: ' + args.only
    qa = ROOT.parent / 'output/comic-panels/qa'
    qa.mkdir(parents=True, exist_ok=True)
    for work in specs:
        path = ROOT / work['source'].lstrip('/')
        assert digest(path) == work['sha256'], 'Source changed: ' + work['id']
        with Image.open(path) as original:
            source = original.convert('RGB')
        assert list(source.size) == work['size']
        coverage = Image.new('1', source.size)
        frame = source.copy()
        out = ROOT / 'assets/images/panels' / work['id']
        if not args.verify:
            out.mkdir(parents=True, exist_ok=True)
        entries = []
        # Some approved seven-panel works use panel 1 as their cover/header.
        panels = [i for i in work['items'] if i['kind'] == 'panel' or i.get('number') is not None]
        assert [i['number'] for i in panels] == list(range(1, len(panels)+1))
        for item in work['items']:
            boxes = [p['box'] for p in item['pieces']] if 'pieces' in item else [item['box']]
            for box in boxes:
                x0,y0,x1,y1 = box
                assert 0 <= x0 < x1 <= source.width and 0 <= y0 < y1 <= source.height
                assert coverage.crop(box).getbbox() is None, 'Overlapping crops: '+item['key']
                ImageDraw.Draw(coverage).rectangle((x0,y0,x1-1,y1-1), fill=1)
            target = out / (item['key'] + '.png')
            crop = Image.open(target).convert('RGB') if args.verify else edited(source_crop(source, item), item)
            if not args.verify:
                crop.save(target)
                crop.save(target.with_suffix('.webp'), 'WEBP', lossless=True, method=6)
            with Image.open(target) as result:
                verify_crop(source, result.convert('RGB'), item)
            with Image.open(target.with_suffix('.webp')) as result:
                assert ImageChops.difference(crop, result.convert('RGB')).getbbox() is None
            if not args.verify:
                draw = ImageDraw.Draw(frame)
                for x0,y0,x1,y1 in boxes:
                    draw.rectangle((x0,y0,x1-1,y1-1), outline='#ff0066', width=3)
                    qa_font = 'C:/Windows/Fonts/arialbd.ttf' if Path('C:/Windows/Fonts/arialbd.ttf').exists() else 'DejaVuSans.ttf'
                    draw.text((x0+8,y0+50), item['key'], font=ImageFont.truetype(qa_font,30), fill='#ff0066', stroke_width=1, stroke_fill='white')
            entries.append({**{k:v for k,v in item.items() if k not in ('box','edits','pieces','canvas_size','reason')}, 'width':crop.width, 'height':crop.height,
                            'png_sha256':digest(target), 'png':'/' + target.relative_to(ROOT).as_posix(),
                            'webp':'/' + target.with_suffix('.webp').relative_to(ROOT).as_posix()})
        assert coverage.getextrema() == (1,1), 'Some source pixels are omitted: ' + work['id']
        assert digest(path) == work['sha256']
        if not args.verify:
            frame.save(qa / (work['id'] + '-bounds.png'))
        manifest[work['id']] = {'title':work['title'], 'source':work['source'], 'items':entries}
        report.append({'id':work['id'], 'source_sha256':work['sha256'], 'panels':len(panels), 'all_source_pixels_covered':True,
                       'png_pixels_verified':True,'lossless_webp_verified':True,'outside_edit_regions_unchanged':True})
    if args.verify:
        assert manifest == saved, 'Asset hashes or metadata changed; rebuild and inspect before accepting'
    else:
        (ROOT / '_data/comic_panels.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        (qa / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
