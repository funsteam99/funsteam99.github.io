"""Validate K–2 release downloads and the rendered course entry."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
import json,re,xml.etree.ElementTree as ET

base=Path('assets/downloads/ai-literacy/k2-cartoon-v3')
manifest=json.loads((base/'release-manifest.json').read_text(encoding='utf-8'))
assert manifest['version']=='3.0'
assert len(manifest['files'])==10
for item in manifest['files']:
    file=base/item['name']
    raw=file.read_bytes()
    assert len(raw)==item['bytes'],file
    assert sha256(raw).hexdigest()==item['sha256'],file
    if file.suffix=='.pdf':
        assert raw.startswith(b'%PDF-') and b'%%EOF' in raw[-100:],file
    if file.suffix=='.docx':
        with ZipFile(file) as z:
            xml=z.read('word/document.xml').decode('utf-8')
            footers=''.join(z.read(n).decode('utf-8') for n in z.namelist() if n.startswith('word/footer'))
            assert '/32' not in xml+footers,file
            assert f'第{item["lesson"]}/8堂' in footers,file
            assert '尚未完成課堂試教或成效驗證' in xml,file
            assert '我的學習單' in xml and '教師觀察評量' in xml,file
            assert '<w:pBdr' not in xml,file
            if item['lesson']==4:
                assert all(s in xml for s in ['找錯標籤','用新例確認','本題設定：大','本題設定：小','看過四張']),file
pack=base/'k2-ai-lessons-01-04-cartoon-v3-teacher-pack.zip'
with ZipFile(pack) as z:
    assert len(z.namelist())==9 and z.testzip() is None
    assert len([n for n in z.namelist() if n.endswith('.docx')])==4
    assert len([n for n in z.namelist() if n.endswith('.pdf')])==4
    for item in manifest['files']:
        if item.get('lesson'):
            assert sha256(z.read(item['name'])).hexdigest()==item['sha256']

site=Path('_site')
if site.exists():
    html=(site/'articles/k2-ai-teacher-handbook/index.html').read_text(encoding='utf-8')
    assert html.count('class="k2-lesson"')==4
    assert '第1～4堂' in html and '尚未完成課堂試教或成效驗證' in html
    assert '既有完整手冊與八堂課程架構' in html
    assert '{{' not in html and '{%' not in html
    for item in manifest['files']:
        assert item['name'] in html,item['name']
    for url in re.findall(r'(?:href|src)="(/[^"#?]*)',html):
        f=site/url.lstrip('/')
        assert f.exists() or (f/'index.html').exists(),url
print('PASS: K2 release checksums, DOCX scope, teacher pack, and built download entry')
