"""Check WebP variants and the picture URLs in the actual Pages build."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import json
import struct
import zlib

root = Path('_site')
manifest = json.loads(Path('_data/image_variants.json').read_text(encoding='utf-8'))
# A previous sound illustration returned HTTP 200 but its PNG stream was corrupt.
sound = (root / 'assets/images/science/sound-transmission.png').read_bytes()
assert sound[:8] == b'\x89PNG\r\n\x1a\n'
offset = 8
compressed = bytearray()
ended = False
while offset < len(sound):
    size = struct.unpack('>I', sound[offset:offset + 4])[0]
    kind = sound[offset + 4:offset + 8]
    data = sound[offset + 8:offset + 8 + size]
    crc = struct.unpack('>I', sound[offset + 8 + size:offset + 12 + size])[0]
    assert zlib.crc32(kind + data) == crc, f'Corrupt sound PNG chunk: {kind}'
    if kind == b'IDAT':
        compressed.extend(data)
    if kind == b'IEND':
        ended = True
        break
    offset += size + 12
assert ended and zlib.decompress(compressed), 'Incomplete sound PNG'
assert '/assets/images/science/sound-transmission.png' in manifest
for original, record in manifest.items():
    assert (root / original.lstrip('/')).is_file(), original
    widths = [v['width'] for v in record['variants']]
    assert widths == sorted(set(widths)) and widths[-1] == record['width']
    for variant in record['variants']:
        data = (root / variant['url'].lstrip('/')).read_bytes()
        assert data[:4] == b'RIFF' and data[8:12] == b'WEBP', variant['url']
        assert len(data) == variant['bytes'], variant['url']

class Sources(HTMLParser):
    count = 0
    def handle_starttag(self, tag, attrs):
        if tag != 'source':
            return
        attrs = dict(attrs)
        if attrs.get('type') != 'image/webp':
            return
        assert attrs.get('sizes'), 'Missing responsive sizes'
        for candidate in attrs['srcset'].split(','):
            url, width = candidate.strip().rsplit(' ', 1)
            assert width.endswith('w') and int(width[:-1]) > 0
            assert (root / unquote(urlsplit(url).path).lstrip('/')).is_file(), url
        self.count += 1

parser = Sources()
for file in root.rglob('*.html'):
    parser.feed(file.read_text(encoding='utf-8'))
assert parser.count >= 25, f'Only {parser.count} responsive pictures rendered'
print(f'PASS: {len(manifest)} original assets, all variants, {parser.count} responsive pictures')
