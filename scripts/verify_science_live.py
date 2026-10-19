"""Verify deployed science pages and decode every original/panel on the real host."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
from urllib.request import urlopen, Request
from io import BytesIO
import argparse, hashlib, json
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
class Reader(HTMLParser):
    def __init__(self):
        super().__init__(); self.inside=False; self.images=[]; self.sources=[]; self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='section' and a.get('class')=='panel-reader': self.inside=True
        if self.inside and tag=='img': self.images.append(a)
        if self.inside and tag=='source': self.sources.append(a)
        if self.inside and tag=='a': self.links.append(a.get('href'))
    def handle_endtag(self,tag):
        if tag=='section': self.inside=False

def verify(base):
    def get(path):
        with urlopen(Request(base+path,headers={'User-Agent':'Shezi-publishing-verifier/1.0'}),timeout=30) as r:
            assert r.status==200
            assert r.url.startswith(base+'/'), 'Unexpected host redirect'
            return r.read()
    index=get('/science/').decode('utf-8')
    data=json.loads((ROOT/'_data/comic_panels.json').read_text('utf-8'))
    queue={w['id']:w for w in json.loads((ROOT/'_operations/science-release-manifest.json').read_text('utf-8'))}
    state=json.loads((ROOT/'_operations/science-release-state.json').read_text('utf-8'))
    results=[]
    for id,release in state.items():
        w=queue[id]; path='/science/'+w['slug']+'/'
        html=get(path).decode('utf-8')
        assert w['title'] in html and path in index
        assert '{{' not in html and '{%' not in html
        parser=Reader(); parser.feed(html)
        expected=data[id]['items']
        assert [i['src'] for i in parser.images]==[i['png'] for i in expected]
        assert len(parser.sources)==len(expected)
        assert w['source'] in parser.links
        card=data[id].get('card_header')
        if card:
            assert card['png'] in index and card['webp'] in index
            png=get(card['png']); webp=get(card['webp'])
            assert hashlib.sha256(png).hexdigest()==card['png_sha256']
            a=Image.open(BytesIO(png)).convert('RGB'); b=Image.open(BytesIO(webp)).convert('RGB')
            assert a.size==b.size==(card['width'],card['height'])
            assert ImageChops.difference(a,b).getbbox() is None
        original=get(w['source'])
        assert hashlib.sha256(original).hexdigest()==w['source_sha256']
        Image.open(BytesIO(original)).verify()
        assets=[]
        for item,rendered,source in zip(expected,parser.images,parser.sources):
            assert (int(rendered['width']),int(rendered['height']))==(item['width'],item['height'])
            assert item['webp'] in source['srcset']
            png=get(item['png']); webp=get(item['webp'])
            assert hashlib.sha256(png).hexdigest()==item['png_sha256']
            a=Image.open(BytesIO(png)).convert('RGB'); b=Image.open(BytesIO(webp)).convert('RGB')
            assert a.size==b.size==(item['width'],item['height'])
            assert ImageChops.difference(a,b).getbbox() is None
            assets.append({'png':base+item['png'],'webp':base+item['webp'],'png_sha256':item['png_sha256'],'size':list(a.size)})
        results.append({'id':id,'url':base+path,'original':base+w['source'],'original_sha256':w['source_sha256'],'panels':assets,'card_header':card,'passed':True})
    return {'verified_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'base_url':base,'releases':results,'passed':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--base-url',default='https://shezi.org.tw'); p.add_argument('--report')
    args=p.parse_args(); result=verify(args.base_url.rstrip('/'))
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.report: Path(args.report).write_text(text,'utf-8')
    print(text)
