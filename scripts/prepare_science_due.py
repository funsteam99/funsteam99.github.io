"""Prepare only due, approved science releases. Dates come from the shared table.

No network calls, pushes, merges or claims of deployment. Repeat runs are idempotent.
The existing ChatGPT Monday task handles PR/check/merge/live verification.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse, hashlib, json, re

TAIPEI = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def plan(root, now):
    text = (root/'_operations/publishing-schedule.md').read_text('utf-8')
    section = text.split('## 自然小探險隊排程',1)[1].split('## 兩端共同使用方式',1)[0]
    rows = []
    for line in section.splitlines():
        if re.match(r'\| 20\d\d-\d\d-\d\d', line):
            cells = [c.strip() for c in line.strip('|').split('|')]
            raw = cells[0]
            if len(raw)==10: raw += ' 09:00'
            when = datetime.strptime(raw,'%Y-%m-%d %H:%M').replace(tzinfo=TAIPEI)
            rows.append((when,*cells[1:]))
    if not rows or len({r[0].date() for r in rows})!=len(rows):
        raise ValueError('Missing or duplicate science schedule dates')
    manifest = json.loads((root/'_operations/science-release-manifest.json').read_text('utf-8'))
    state_path = root/'_operations/science-release-state.json'
    state = json.loads(state_path.read_text('utf-8')) if state_path.exists() else {}
    due=[]
    for work in manifest:
        matches=[r for r in rows if (work['title'] in r[1] or work['id']=='butterfly-2026' and '蝴蝶生命循環' in r[1])]
        if len(matches)!=1: raise ValueError('Missing/duplicate title: '+work['id'])
        when,title,status,executor=matches[0]
        if executor!='ChatGPT': raise ValueError('Wrong executor: '+work['id'])
        if when.weekday()!=0: raise ValueError('Science date must be Monday')
        if when>now: continue
        source=root/work['source'].lstrip('/')
        template=root/work['template']
        if sha(source)!=work['source_sha256'] or sha(template)!=work['template_sha256']:
            raise ValueError('Approved source/template changed: '+work['id'])
        page=root/'science'/f"{work['slug']}.html"
        index=(root/'science/index.html').read_text('utf-8')
        if work['id'] in state:
            if not page.exists() or page.read_bytes()!=template.read_bytes() or work['card'].strip() not in index:
                raise ValueError('Published/prepared page or index drift: '+work['id'])
            continue
        if '已發布' in status:
            raise ValueError('Published table row lacks matching release state: '+work['id'])
        if page.exists() and work['id']!='butterfly-2026':
            raise ValueError('Existing page requires reconciliation: '+str(page))
        due.append((work,when))
    return due,state

def prepare(root,now):
    due,state=plan(root,now)
    index_path=root/'science/index.html'
    index=index_path.read_text('utf-8')
    # Validate every work before writing any file.
    for work,when in due:
        if work['id']=='butterfly-2026':
            pattern=r'    <article class="science-card">\s*<a href="\{\{ \'/science/butterfly-life-cycle/\'.*?</article>\s*'
            index,count=re.subn(pattern,'',index,flags=re.S)
            if count!=1: raise ValueError('Expected exactly one existing butterfly card')
        marker='    <article class="science-card"'
        at=index.index(marker)
        index=index[:at]+work['card']+index[at:]
        state[work['id']]={'scheduled_at':when.isoformat(),'status':'prepared','url':'https://shezi.org.tw/science/'+work['slug']+'/', 'source_sha256':work['source_sha256']}
    for work,_ in due:
        (root/'science'/f"{work['slug']}.html").write_bytes((root/work['template']).read_bytes())
    if due:
        index_path.write_text(index,'utf-8')
        (root/'_operations/science-release-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n','utf-8')
    return [w['id'] for w,_ in due]

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    now=datetime.now(TAIPEI)
    result=prepare(ROOT,now) if args.apply else [w['id'] for w,_ in plan(ROOT,now)[0]]
    print(json.dumps({'taipei_time':now.isoformat(),'prepared' if args.apply else 'due':result},ensure_ascii=False))
