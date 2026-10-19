# 自然小探險隊 — 素材集中索引（2026-10-14）

用途：ChatGPT 與 Codex 協作時先看本表，再核對官網及素材實體。**找到 ChatGPT 檔案庫附件，不等於圖片已上傳 GitHub，也不等於官網已發布。**

| 預定日期（台灣09:00） | 題名 | ChatGPT 檔案庫找到的圖檔 | 素材狀態 | 發布狀態／待辦 |
|---|---|---|---|---|
| 2026-10-12 | 彩虹為什麼會出現？ | `彩虹分光魔術：自然科學探險隊.png`（Library ID `libfile_ac4e5eb793e08191a4e67173c7bf3422`，2026-10-05） | **已找到原始附件**，未確認 GitHub 中有圖片位址 | **逾期優先核對／補發**。先取得圖片實體上傳至官網儲存庫，再做發布頁及連結檢查；不能重發已有頁面 |
| 2026-10-19 | 密度是什麼？一樣大，不一定一樣重！ | `七格漫畫探索密度奧秘.png`（Library ID `libfile_baac5d7b56348191a61135cbc6838863`，2026-10-05） | **已找到原始附件**，未確認已同步 | 待發布 |
| 2026-10-26 | 蝴蝶生命循環 | `自然小探險隊：蝴蝶生命循環.png`（Library ID `libfile_d2c2e1bb76048191b646cce8e3484989`，2026-10-05） | **已找到原始附件**，未確認是否網站最新版 | 官網已有對應內容線索；只更新舊頁，不另建同名頁 |
| 2026-11-02 | 日食是什麼？ | 2026-10-14 使用者已在當前對話重新上傳日食七格定稿圖（會話 file ID `file_00000000e2b48206bc45698fe4a16829`） | **定稿圖已收到；待同步 GitHub** | 待發布；須先核實太陽觀測安全說明 |
| 2026-11-09 | 月食是什麼？ | 2026-10-14 使用者已在當前對話重新上傳月食七格定稿圖（會話 file ID `file_000000000c488206bbbea001c25440fa`） | **定稿圖已收到；待同步 GitHub** | 待發布 |
| 2026-11-16（建議） | 冰水杯為什麼會流汗？ | 2026-10-14 本次對話生成七格漫畫；會話圖檔 ID `file_00000000b03c82098568c28aa0d80b82` | **使用者已確認定稿；圖片實體在本次對話，尚待同步 GitHub** | 排定 11/16；發布前核對圖片版本、官網是否重複、網站部署 |

已發布不重發：`https://shezi.org.tw/science/sound-transmission/`（聲音是怎麼傳播的？；共用排程表記錄2026-10-05）。

## 素材交接標準

1. ChatGPT 檔案庫 Library ID 只用來**尋找素材**，不是能由 Codex 或一般瀏覽器直接下載的公開連結。
2. 圖片實體應進入 GitHub 儲存庫（或可部署資產庫），並記錄確切 repository path、Git commit SHA、最後校正版本與素材審核狀態。
3. 每篇記錄：標題、日期、分類 `science/`、主圖路徑、文章頁面路徑、GitHub PR、審核狀態、官網實際連結。
4. 如無實體圖檔或未經審核，不得僅憑本表發布；不能用臨時生成圖取代已核准圖。
5. 發布前核對 `science/index.html`、既有頁面及正式站，避免重複；部署驗證成功後才標「已發布」。
6. 以 `_operations/publishing-schedule.md` main 分支為日期主表。本索引為素材線索，不會自行觸發任何排程。

## 2026-10-14 使用者確認事項

- 日食、月食的更正定稿存在於先前對話，且 2026-10-14 使用者已在當前對話重新提供兩張實體定稿圖片；不需要重做，下一步僅需同步 GitHub 並核對官網。
- 冰水杯流汗的漫畫由使用者在 2026-10-14 明確確認「已經定稿」；採用該版本，不自行重繪。前述內容審核為編輯建議，不取代使用者的定稿決定。

## 2026-10-14 歷史阻礙（2026-10-19 已解決）

當時 GitHub 連接器在該操作環境可寫入 UTF-8 文字檔，但無法直接將 Library PNG 二進位附件轉存進 GitHub；本次先提供精確 ID 和檔名供素材交接。圖片尚未成功同步到儲存庫時，不得將素材狀態標成「已同步」。

## 2026-10-19 原圖同步與逐格交接

已從登入的ChatGPT Library下載「自然小探險隊-六篇定稿素材.zip」，ZIP完整性檢查通過；採包內已定稿原圖，沒有重繪或改字。六篇原圖、逐格PNG及無損WebP隨本次修復PR存入儲存庫。原圖SHA256與文章範本校驗值另見 `science-release-manifest.json`；逐格座標、原圖hash在 `_data/comic_panel_specs.json`，輸出圖片與hash在 `_data/comic_panels.json`。

素材包SHA256：`0719a5d50f5ece277f183e62df59cb4802fcaca10833a5bfb4689723ba46015e`。Library來源ID仍作索引線索；發布直接讀GitHub素材，不再等待附件轉移或例行人工審核。

| 原定日期 | 題名 | 真正原圖repository path | 原圖SHA256 | 文章路徑 | 逐格ID |
|---|---|---|---|---|---|
| 2026-10-12 | 彩虹為什麼會出現？ | `assets/images/science-approved/rainbow.png` | `6960a6e931e268780a6846be2e32d71a223f576a80dcfd428d8a27875ed2ce14` | `science/rainbow.html` | `rainbow` |
| 2026-10-19 | 密度是什麼？一樣大，不一定一樣重！ | `assets/images/science-approved/density.png` | `a83c77907795e42cc0075bcf065d5bd61352f3cb8f8d6c1317c512c3e5e2b18a` | `science/density.html` | `density` |
| 2026-10-26 | 蝴蝶生命循環 | `assets/images/science-approved/butterfly-2026.png` | `e197e44d5906fe4e77ee11310ba653ddb469baf2ee032e9ee2793119194a8c48` | `science/butterfly-life-cycle.html` | `butterfly-2026` |
| 2026-11-02 | 日食是什麼？ | `assets/images/science-approved/solar-eclipse.png` | `b687825ab5e8304f52f2248bd927877a121f89b28bef70c7b4374e4578f3fb1f` | `science/solar-eclipse.html` | `solar-eclipse` |
| 2026-11-09 | 月食是什麼？ | `assets/images/science-approved/lunar-eclipse.png` | `29ff03c5ecfafa2da8ef32438a101ad9e1d637da470be936381dfe289d485594` | `science/lunar-eclipse.html` | `lunar-eclipse` |
| 2026-11-16 | 冰水杯為什麼會流汗？ | `assets/images/science-approved/condensation.png` | `62c2f8e23ce9d95a8c3fdeff9c65b2a2a70394b553d171f30ec4b1927b634eec` | `science/why-cold-cups-sweat.html` | `condensation` |

未到期文章僅存於 `_operations/science-pages/`，蝴蝶10/26只更新舊頁；彩虹、密度隨本次PR補發。此處素材同步不等於部署完成，正式網址驗證後才更新主日期表。每次發布依 `science-publishing-runbook.md`，既有主排程不另新增。
