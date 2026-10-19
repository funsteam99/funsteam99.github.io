"""Isolated checks: no early releases, due catchup, idempotency and drift guards."""
import importlib.util, tempfile, shutil, json
from datetime import datetime
from pathlib import Path
spec=importlib.util.spec_from_file_location('release',Path(__file__).with_name('prepare_science_due.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(dir=m.ROOT.parent) as tmp:
    root=Path(tmp)/'repo'
    for name in ['_operations','science','assets/images/science-approved']:
        shutil.copytree(m.ROOT/name,root/name)
    state=root/'_operations/science-release-state.json'
    if state.exists(): state.unlink()
    for slug in ['rainbow','density','solar-eclipse','lunar-eclipse','why-cold-cups-sweat']:
        (root/'science'/f'{slug}.html').unlink(missing_ok=True)
    # Restore pre-release index from git; preserve the original butterfly page.
    import re
    original=(root/'science/index.html').read_text('utf-8')
    original=re.sub(r'[ \t]*<article class="science-card" data-science-id="[^"]+">.*?</article>','',original,flags=re.S)
    if "id='butterfly'" not in original:
        original=original.replace('    <article class="science-card"', '''    <article class="science-card"><a href="{{ '/science/butterfly-life-cycle/' | relative_url }}">{% include comic-header.html id='butterfly' %}</a><h2>蝴蝶的生命循環</h2></article>
    <article class="science-card"''',1)
    (root/'science/index.html').write_text(original,'utf-8')
    table=root/'_operations/publishing-schedule.md'
    text=table.read_text('utf-8')
    lines=[]
    for line in text.splitlines():
        if re.match(r'\| 2026-(10-(12|19|26)|11-(02|09|16)) 09:00',line):
            cells=line.split('|'); cells[3]=' 待發布 '; line='|'.join(cells)
        lines.append(line)
    table.write_text('\n'.join(lines)+'\n','utf-8')
    def at(s): return datetime.fromisoformat(s).replace(tzinfo=m.TAIPEI)
    assert m.prepare(root,at('2026-10-12T08:59:59'))==[]
    assert m.prepare(root,at('2026-10-19T09:00:00'))==['rainbow','density']
    assert m.prepare(root,at('2026-10-19T09:00:00'))==[]
    assert not (root/'science/solar-eclipse.html').exists()
    assert m.prepare(root,at('2026-10-26T08:59:59'))==[]
    assert m.prepare(root,at('2026-10-26T09:00:00'))==['butterfly-2026']
    assert (root/'science/index.html').read_text('utf-8').count('<h2>蝴蝶生命循環</h2>')==1
    assert m.prepare(root,at('2026-11-02T09:00:00'))==['solar-eclipse']
    assert m.prepare(root,at('2026-11-09T09:00:00'))==['lunar-eclipse']
    assert m.prepare(root,at('2026-11-16T09:00:00'))==['condensation']
    assert m.prepare(root,at('2026-11-23T09:00:00'))==[]
    page=root/'science/density.html'; page.write_text('drift','utf-8')
    try: m.prepare(root,at('2026-11-23T09:00:00'))
    except ValueError: pass
    else: raise AssertionError('Drift was not blocked')
print('PASS: due dates, catchup, future isolation, all six releases, butterfly replacement, idempotency and drift')
