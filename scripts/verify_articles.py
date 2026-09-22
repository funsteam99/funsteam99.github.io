"""Validate the actual GitHub Pages build without deploying it."""
from pathlib import Path
import re
from urllib.parse import unquote

root = Path("_site")
home = (root / "index.html").read_text(encoding="utf-8")
archive = (root / "articles/index.html").read_text(encoding="utf-8")
old_post = (root / "articles/exam-review-guide/index.html").read_text(encoding="utf-8")
post = (root / "articles/exam-review-battle/index.html").read_text(encoding="utf-8")
placement = (root / "articles/placement-test-g1-g2/index.html").read_text(encoding="utf-8")
title = "考前複習大作戰｜找出弱點、做對練習，讓複習更有效"
for html in (home, archive, old_post, post, placement):
    assert "{{" not in html and "{%" not in html, "Unrendered Liquid"
for html in (home, archive, post):
    assert title in html
news = home.split('<section id="news"')[1].split("</section>")[0]
articles = home.split('<section id="articles"')[1].split("</section>")[0]
assert title not in news, "Education article displaced news"
assert "2025年10月 最新消息" in news
assert "親子春聯 DIY" in news and "現在加入會員" in news
assert articles.count('aria-label="閱讀全文：') >= 1
assert "/articles/exam-review-guide/" in articles and "/articles/exam-review-guide/" in archive
assert "/articles/exam-review-battle/" in articles and "/articles/exam-review-battle/" in archive
assert "/articles/placement-test-g1-g2/" in articles and "/articles/placement-test-g1-g2/" in archive
assert "2026.09.22" in articles and "2026-09-22" in post, "Publication date must use Taiwan timezone"
assert "2026-09-14" in old_post, "Original article must retain its publication date"
assert "考前不再從第一頁讀到最後一頁：中小學生高效複習指南" in old_post
assert "考前 7 天作戰計畫" in post and "考前終極檢查表" in post
assert "60 分鐘" in post and "不要只用「粗心」" in post
assert "國小一至六年級（G1–G6）" in placement
homepage = (root / "index.html").read_text(encoding="utf-8")
homepage_data = (root / "_data/homepage.yml").read_text(encoding="utf-8")
assert "國小一至六年級（G1–G6）起點檢測卷" in homepage
assert "國小一至六年級起點檢測卷 (G1–G6)" in homepage_data
for grade in range(1, 7):
    assert f"下載 G{grade} 學生作答卷" in placement
    assert f"下載 G{grade} 家長解答與評估手冊" in placement
assert "此篇改由首頁" not in home + archive
for html in (home, archive, old_post, post, placement):
    for url in re.findall(r'(?:href|src)="(/[^"#?]*)', html):
        path = root / unquote(url).lstrip("/")
        assert path.exists() or (path / "index.html").exists(), f"Missing local URL: {url}"
print("PASS: Pages build, article routes, retained news, complete content, local links")
