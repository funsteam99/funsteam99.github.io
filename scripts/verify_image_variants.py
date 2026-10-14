"""Check WebP variants and the picture URLs in the actual Pages build."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import json

root = Path('_site')
manifest = json.loads(Path('_data/image_variants.json').read_text(encoding='utf-8'))
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
