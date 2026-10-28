# K–2 前四堂卡通圖卡版發布紀錄

版本：v3.0。日期：2026-10-28。時區：Asia/Taipei。

本次依使用者授權，改善並發布八堂 AI 素養系列中的第1～4堂，不替換既有完整八堂手冊。沿用正式課程頁 `/articles/k2-ai-teacher-handbook/`，保留原文章日期與原下載網址。

## 內容與版面修訂

- 全部正文、銜接與頁尾統一八堂課架構。
- 每堂8頁，分開教師總覽、指引、圖卡、活動、學習單、答案、觀察表與海報；學生頁放大字級，圖卡保留可剪裁卡號，分類牌以文字與符號支援黑白列印。
- 第3堂增加天氣與翅膀反例，保留原預測與新觀察，不再只重複第1堂水果活動。
- 第4堂補錯誤標籤辨識；分清 A 組、B 組與未見新例；修正學習單前提，觀察表直接對應資料涵蓋、方法限制、標籤正確性與新例確認。大小明列教材設定，答案標籤另剪並遮住。
- 提供4份逐堂 PDF、4份可編輯 Word、32頁合併 PDF，以及含逐堂8檔與使用說明的教師包 ZIP。
- 保留「尚未完成課堂試教或成效驗證」與無設備、學生不需個人帳號、個資保護及紙上類比說明。

## 發布前驗證

四份修訂 Word 均以 Microsoft Word 匯出 PDF，每堂8頁。已檢視全部32頁頁面、核對頁序及學生題目與教師答案，修正溢頁、標題邊線與圖卡裁切邊界。PDF 字型均有嵌入；合併 PDF 為32頁，含四堂書籤。教師包可正常解壓且檔案與逐堂下載一致。

附件內容與 SHA256 清單：`assets/downloads/ai-literacy/k2-cartoon-v3/release-manifest.json`。`scripts/verify_k2_cartoon.py` 檢查附件版本、hash、Word八堂定位、教師包與建置後下載入口，納入既有 Verify Jekyll articles 流程。

本紀錄不宣稱完成課堂試教。部署及正式網址驗證結果另以驗證摘要記錄；不得以本地匯出或 PR 建置代替正式部署驗收。

## 正式發布驗收

2026-10-28 14:25:28 +08:00，正式課程頁、4張預覽、列印指引及10個新版附件均通過驗證；1440、768、390、320像素無橫向溢出。10檔HTTP 200、大小及SHA256均符合發布manifest；既有完整八堂Word／PDF仍可下載。

發布PR：https://github.com/funsteam99/funsteam99.github.io/pull/37 。部署commit：`2fb25efcd75de4414ebe60c9051bf8310dfc9cd4`。Pages部署成功：https://github.com/funsteam99/funsteam99.github.io/actions/runs/40643571659 。驗證證據：`k2-cartoon-verification-20261028.json`。

正式入口：https://shezi.org.tw/articles/k2-ai-teacher-handbook/ 。本次更新既有文章，保留2026-10-16原文章日期；新版教材明列2026-10-28更新。
