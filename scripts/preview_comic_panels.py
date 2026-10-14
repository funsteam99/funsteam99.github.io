from pathlib import Path
import json,html
root=Path(__file__).resolve().parents[2]
site=root/'serial-publish'
manifest=json.loads((site/'_data/comic_panels.json').read_text(encoding='utf-8'))
out=root/'output/comic-panels'
out.mkdir(parents=True,exist_ok=True)
parts=[]
for id,w in manifest.items():
    figures=[]
    for i in w['items']:
        url='../../serial-publish'+i['png']
        number=f'<figcaption class="panel-reader__number">{i["number"]}</figcaption>' if i.get('show_number') else ''
        figures.append(f'<figure class="panel-reader__item">{number}<a href="{url}" target="_blank"><img src="{url}" width="{i["width"]}" height="{i["height"]}" alt="{html.escape(i["alt"])}" loading="lazy"></a></figure>')
    parts.append(f'<article id="{id}"><h2>{html.escape(w["title"])}</h2><p><a href="qa/{id}-bounds.png" target="_blank">原圖裁切框對照</a> · <a href="../../serial-publish{w["source"]}" target="_blank">未修改原圖</a></p><section class="panel-reader">'+''.join(figures)+'</section></article>')
nav=''.join(f'<a href="#{id}">{html.escape(w["title"])}</a>' for id,w in manifest.items())
css=(site/'assets/css/comic-reader.css').read_text(encoding='utf-8')
(out/'index.html').write_text('''<!doctype html><html lang="zh-TW"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>漫畫分格本機預覽</title><style>'''+css+'''body{margin:0;background:#eef3f6;color:#162c40;font-family:system-ui,sans-serif}header{padding:20px;max-width:960px;margin:auto}h1{font-size:25px}nav{display:flex;gap:8px;flex-wrap:wrap}nav a,button{background:white;border:1px solid #b9cbd6;border-radius:6px;padding:8px;color:#153c56}main{box-sizing:border-box;max-width:760px;margin:20px auto;padding:12px;background:white}main.phone{max-width:375px}article{border-bottom:1px solid #ddd;margin-bottom:40px}h2{font-size:22px}p{line-height:1.7}a{color:#18506c}</style><header><h1>漫畫分格本機預覽</h1><p>此為本機內容預覽，尚未發布。點選裁切框對照可核對原圖；點選單格可看原尺寸。</p><p><button onclick="document.querySelector('main').classList.toggle('phone')">切換 375px 手機寬度／一般寬度</button></p><nav>'''+nav+'</nav></header><main class="phone">'+''.join(parts)+'</main></html>',encoding='utf-8')
print(out/'index.html')
