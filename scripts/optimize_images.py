"""Generate WebP variants without changing originals. Validated with Pillow 12.3.0.

Run from the repository root: python scripts/optimize_images.py
"""
from pathlib import Path
import json
from PIL import Image, ImageOps

root = Path(__file__).resolve().parents[1]
manifest = {}
before = after = 0
for folder in ('pics', 'assets/images'):
    for path in sorted((root / folder).rglob('*')):
        if path.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
            continue
        with Image.open(path) as source:
            try:
                image = ImageOps.exif_transpose(source).convert('RGBA' if 'A' in source.getbands() else 'RGB')
            except OSError as error:
                print(f'SKIP unreadable original: {path.name}: {error}')
                continue
            width, height = image.size
            variants = []
            for target in sorted({min(640, width), min(1280, width), width}):
                resized = image if target == width else image.resize((target, round(height * target / width)), Image.Resampling.LANCZOS)
                output = path.with_name(f'{path.stem}-{target}.webp')
                resized.save(output, 'WEBP', quality=85, method=6)
                variants.append({'url': '/' + output.relative_to(root).as_posix(), 'width': target, 'bytes': output.stat().st_size})
            key = '/' + path.relative_to(root).as_posix()
            manifest[key] = {'width': width, 'height': height, 'original_bytes': path.stat().st_size, 'variants': variants, 'full': variants[-1]['url']}
            before += path.stat().st_size
            after += variants[-1]['bytes']
            print(f'{key}: {path.stat().st_size:,} -> {variants[-1]["bytes"]:,} bytes')
(root / '_data/image_variants.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Total original/full WebP: {before:,} -> {after:,} bytes ({100 * (1 - after / before):.1f}% less)')
