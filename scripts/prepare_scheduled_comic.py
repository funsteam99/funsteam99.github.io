"""Prepare an approved due episode using per-image panel specs. Never pushes or schedules."""
from pathlib import Path
import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from datetime import date

ROOT = Path(__file__).resolve().parents[1]

def prepare(number, title, publication_date, source):
    assert re.fullmatch(r'0[2-8]', number), 'Unapproved episode'
    date.fromisoformat(publication_date)
    marker = 'weekly-journey-ep' + number
    work_id = 'journey-' + number
    source = Path(source)
    specs_path = ROOT / '_data/comic_panel_specs.json'
    specs = json.loads(specs_path.read_text(encoding='utf-8'))
    approved = json.loads((ROOT / '_operations/scheduled-comic-panel-specs.json').read_text(encoding='utf-8'))
    selected = [w for w in approved if w['id'] == work_id]
    if len(selected) != 1:
        raise ValueError('No unique approved panel specification; refusing whole-page fallback')
    spec = selected[0]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == spec['sha256'], 'Scheduled original version differs from approved panel coordinates'
    assert spec['source'] == '/assets/images/comics/' + marker + '.png'
    target = ROOT / spec['source'].lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != target.resolve():
        shutil.copyfile(source, target)
    specs = [w for w in specs if w['id'] != work_id] + [spec]
    specs_path.write_text(json.dumps(specs, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    builder = ROOT / 'scripts/build_comic_panels.py'
    subprocess.run([sys.executable, str(builder), '--only', work_id], check=True)
    subprocess.run([sys.executable, str(builder), '--only', work_id, '--verify'], check=True)
    page = ROOT / 'modern-journey/index.html'
    text = page.read_text(encoding='utf-8')
    block = f'''    <article class="comic-feature" id="{marker}">
      <header class="comic-feature__header">
        <p class="text-sm font-bold text-amber-700 tracking-widest">現代西遊大冒險・第 {int(number)} 集・{publication_date}</p>
        <h2 class="text-3xl md:text-4xl font-black text-slate-900 mt-3">《{html.escape(title)}》</h2>
      </header>
      {{% include comic-reader.html id='{work_id}' %}}
    </article>'''
    pattern = r'    <article\b[^>]*\bid="' + re.escape(marker) + r'"[^>]*>.*?</article>'
    existing = list(re.finditer(pattern, text, re.S))
    assert len(existing) <= 1, 'Duplicate episode article'
    if existing:
        text = re.sub(pattern, lambda m: block, text, count=1, flags=re.S)
    else:
        anchor = '    <article class="comic-feature"'
        assert anchor in text, 'Episode insertion point missing'
        text = text.replace(anchor, block+'\n'+anchor, 1)
    page.write_text(text, encoding='utf-8')
    index_path = ROOT / '_data/journey_episodes.json'
    index = json.loads(index_path.read_text(encoding='utf-8'))
    index = [i for i in index if i['id'] != work_id]
    index.append({'id':work_id, 'number':int(number), 'title':title, 'anchor':marker})
    index.sort(key=lambda i:i['number'])
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Prepared and verified panels + index: '+work_id)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--episode', required=True)
    p.add_argument('--title', required=True)
    p.add_argument('--date', required=True)
    p.add_argument('--source', required=True)
    a = p.parse_args()
    prepare(a.episode, a.title, a.date, a.source)
