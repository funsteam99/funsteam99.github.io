# 自然小探險隊自動發布操作

唯一喚醒：ChatGPT 主排程 `6ac386f54bc081918c6698b94f23d468`，每週一台灣09:00。不要新增第二個排程。使用者已授權定稿、分支、PR、測試、合併與部署，不再要求例行人工審核。技術檢查不取代或重開內容核定。

## 已完成的素材交接

六篇真正PNG與全部逐格PNG／無損WebP均在main；確切路徑、SHA256、文章範本與列表卡片見 `science-release-manifest.json`。已核定原圖不重繪。Library只保留來源線索，發布不再依賴Library下載權限。尚未到期的範本在 `_operations/science-pages/`，不會成為公開文章；不要提前複製到science/。

## 每次執行

1. 先讀main的 `publishing-schedule.md`、`science-asset-inventory.md`、`science-release-manifest.json`、`science-release-state.json`，核對科學目錄、相關PR與正式站。日期僅採main日期表，不用manifest內日期快照覆蓋主表。讀取失敗、重複日期、內容衝突、執行端不是ChatGPT時停止並準確報錯。
2. 僅處理台灣時間已到的列。逾期補發保留原排週次，不移走後續核定篇目；多篇逾期可同次追回，不改成同一個預定週次。沒有到期項目則不改檔。聲音已發布不重發；蝴蝶只覆寫 `science/butterfly-life-cycle.html`，不可新增第二個網址。
3. 有終端時：更新main後執行 `python scripts/prepare_science_due.py --apply`，此程式會驗證原圖／範本hash、日期與已有狀態，準備到期文章、列表與prepared狀態，不會自行推送或聲稱部署成功。
4. 只有GitHub連接器時：從main讀取manifest中該篇template全文，建立分支，在分支新增或更新 `science/<slug>.html`，內容完全採範本；以manifest的card加入science/index.html。蝴蝶先移除原有舊版card，再加入新版，保留既有網址。`_data/comic_panels.json` 已含六篇完整素材資料，無需生成或上傳二進位。將該篇加入science-release-state.json，格式參照現有列，scheduled_at取主表含+08:00，status先標prepared。核對所有圖片檔實際存在，勿憑路徑猜測。
5. 接續同題未完成PR，或建立分支PR；不要直接寫main。等待 `Verify Jekyll articles / build` 成功，核對diff只包含已到期文章、相關目錄／發布紀錄。通過後自行合併，毋須使用者例行核准。檢查不通過先修正，不略過。
6. 等待該合併commit的GitHub Pages部署成功。從 `https://shezi.org.tw/science/<slug>/` 及science/目錄核對標題、逐格順序、完整原圖入口。逐一取得該篇所有PNG、WebP與原圖，確認HTTP成功、圖片可解碼，與manifest的PNG SHA256／尺寸一致。不能以「已建立PR」「已合併」代替發布驗收。
7. 驗收成功後另以分支PR與檢查流程更新主表為已發布，記錄實際台灣驗證時間、原排日期、正式URL、PR與部署commit；state設verified，增加verified_at、deployment_commit、pr。補發時間不能冒充原排日期。素材索引記錄實際路徑、原圖hash與正式網址。若兩篇同次補發，在表上各記其原定週次。
8. 僅在完成、失敗或真正需要使用者處理時回報。真實權限或檔案缺失需具體說明失敗步驟和錯誤，不問「要不要繼續」、不再送例行內容審核、不假稱成功。

## 可重跑與測試

`python scripts/test_science_due.py` 在隔離副本檢查六篇日期、提前阻擋、逾期追回、蝴蝶覆寫、重跑與內容變更防護。每個PR均執行既有官網建置／文章／圖片／逐格閱讀檢查，加上此日期測試與六篇原圖裁切像素驗證。部署後才更新日期表；若中途失敗，依prepared/verified狀態接續正式站驗證，不重複建稿。

GitHub Actions目前不能自行建立PR（can_approve_pull_request_reviews=false），因此沿用已授權的ChatGPT主排程與GitHub連接器來建立、檢查、合併PR；不擴大權限、不新增PAT或第二個喚醒排程。
