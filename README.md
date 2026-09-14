# 社子文教基金會正式官網

正式程式庫：https://github.com/funsteam99/funsteam99.github.io
正式網域：https://shezi.org.tw （根目錄 CNAME）

## 產生方式

GitHub Pages 從 main 分支建置 Jekyll。index.html 的 front matter 指定 default 版型，
首頁讀取 _data/homepage.yml；導覽及頁尾讀取 _data/site_settings.yml。
_layouts/default.html 載入 Tailwind CDN 與全站 CSS，_layouts/post.html 包覆 Markdown 文章。
_config.yml 使用 kramdown，並為 posts 預設 post 版型。
smart-ai-lab/index.html 是獨立靜態頁，index_old.html 是保留的舊首頁。

## 新增教育文章

在 _posts 新增 YYYY-MM-DD-slug.md，例如：

```yaml
---
title: "文章標題"
date: 2026-09-14 00:00:00 +0800
section: articles
category: 學習方法
author: 社子文教基金會
permalink: /articles/your-article-slug/
description: "適合首頁卡片的短摘要"
---
正文使用 Markdown。
```

section: articles 是教育文章的必要欄位；首頁依日期顯示最新三篇，
/articles/ 顯示全部教育文章。未標此欄位的舊 posts 繼續出現在最新消息。
published: false 的草稿不發布。未來日期文章依 Jekyll 預設不發布，日期到達後仍須觸發建置。
圖片可選擇加上 image 與 image_alt，檔案放在 pics/uploads。
現有 /admin 的集合仍為最新消息；教育文章目前直接使用 GitHub Markdown 編輯，
不變更現有 git-gateway 後台設定。

## 預覽與驗證

每個 PR 執行 Verify Jekyll articles 工作流程，使用官方 actions/jekyll-build-pages
建置並檢查實際輸出的文章路徑、既有公告、完整文章內容及站內連結。
成功後下載 site-preview artifact，使用任意靜態伺服器開啟，
檢查 /、/articles/、/articles/exam-review-guide/。
此工作流程不部署網站。

本機有 Ruby 時，也可使用 bundle install 與 bundle exec jekyll serve。
Gemfile 的 Jekyll 4.3.4 與 GitHub Pages 內建版本不同，
正式相容性以 PR 的 GitHub Pages 建置為準。

修改先在獨立分支與 PR 審查，合併 main 才會觸發正式 Pages 發布。
考前指南的列印樣式僅列出 Check 卡，可使用瀏覽器列印功能。
