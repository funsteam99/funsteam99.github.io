"""Check the generated resource page and real download, without deployment."""
from pathlib import Path
import re

root = Path('_site')
page = (root / 'ai-literacy/index.html').read_text(encoding='utf8')
home = (root / 'index.html').read_text(encoding='utf8')
news = (root / 'news/ai-literacy-lessons/index.html').read_text(encoding='utf8')
assert '{{' not in page and '{%' not in page
assert page.count('class="ai-lesson"') == 6
assert '學習資源' in page and '/ai-literacy/' in home and '/ai-literacy/' in news
for number in (3, 5, 7, 9, 11, 13):
    assert f'.pdf#page={number}' in page
for link in re.findall(r'(?:href|src)="(/[^"#?]*)', page):
    target = root / link.lstrip('/')
    assert target.exists(), link
pdf = root / 'assets/downloads/ai-literacy/ai-literacy-lessons-v1.1.pdf'
assert pdf.read_bytes().startswith(b'%PDF-')
assert pdf.stat().st_size > 10000
assert 'AI 素養</a>' not in page.split('<main')[0], 'Unexpected top-level navigation'
print('PASS: AI literacy page, six lessons, resource entry, announcement, PDF and local links')
