"""Verify the rendered Jekyll reader, assets, order, and numbering."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json

root = Path('_site')
data = json.loads(Path('_data/comic_panels.json').read_text(encoding='utf-8'))

class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images, self.numbers, self.originals = [], [], []
        self.in_reader = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and attrs.get('class') == 'panel-reader':
            self.in_reader = True
        if self.in_reader and tag == 'img' and '/assets/images/panels/' in attrs.get('src', ''):
            self.images.append((attrs['src'], int(attrs['width']), int(attrs['height'])))
            assert attrs.get('alt') and attrs.get('loading') in ('eager','lazy')
        if tag == 'figcaption' and attrs.get('class') == 'panel-reader__number':
            self.numbers.append(True)
        if tag == 'a':
            self.originals.append(attrs.get('href'))
    def handle_endtag(self, tag):
        if tag == 'section':
            self.in_reader = False

episodes = json.loads(Path('_data/journey_episodes.json').read_text(encoding='utf-8'))
assert [i['number'] for i in episodes] == sorted(set(i['number'] for i in episodes))
pages = {'modern-journey':[i['id'] for i in reversed(episodes)],
         'science/sound-transmission':['sound'], 'science/butterfly-life-cycle':['butterfly'],
         'science/why-four-seasons':['seasons'], 'science/battery-lightbulb':['battery'],
         'science/how-airplanes-fly':['airplanes']}
state_path = Path('_operations/science-release-state.json')
if state_path.exists():
    for comic_id, release in json.loads(state_path.read_text(encoding='utf-8')).items():
        page = release['url'].split('https://shezi.org.tw/',1)[1].rstrip('/')
        pages[page] = [comic_id]
for page, ids in pages.items():
    text = (root / page / 'index.html').read_text(encoding='utf-8')
    parser = Reader()
    parser.feed(text)
    expected = [i for id in ids for i in data[id]['items']]
    assert parser.images == [(i['png'],i['width'],i['height']) for i in expected], page
    assert len(parser.numbers) == sum(bool(i.get('show_number')) for i in expected), page
    for id in ids:
        assert data[id]['source'] in parser.originals
    for i in expected:
        assert hashlib.sha256((root / i['png'].lstrip('/')).read_bytes()).hexdigest() == i['png_sha256']
        assert (root / i['webp'].lstrip('/')).is_file()
    assert 'comic-reader.css' in text
    for id in ids:
        card = data[id].get('card_header')
        if card:
            index = (root / 'science/index.html').read_text(encoding='utf-8')
            assert card['png'] in index and card['webp'] in index
            assert hashlib.sha256((root/card['png'].lstrip('/')).read_bytes()).hexdigest() == card['png_sha256']
    if page == 'modern-journey':
        for episode in episodes:
            assert f'href="#{episode["anchor"]}"' in text
            assert f'id="{episode["anchor"]}"' in text
        import re
        article_ids = re.findall(r'<article class="comic-feature" id="weekly-journey-ep(\d+)"', text)
        assert sorted(map(int, article_ids)) == [i['number'] for i in episodes], 'Every published episode must have an index and a panel reader'
assert '親子一起動手做' in (root / 'science/sound-transmission/index.html').read_text(encoding='utf-8')
print(f'PASS: {len(data)} comics; rendered order, numbers, asset hashes, originals and supplementary text')
