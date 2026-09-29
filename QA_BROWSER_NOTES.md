# Browser QA Notes

日期：2026-09-08

初次桌面版瀏覽器驗證通過：`http://127.0.0.1:8091/` 可載入，頁面標題為「校鮮集｜多校食品團購管理平台（展示原型）」。首屏可見品牌、導覽、候選名稱標籤、主要 CTA、100 校展示數據與企業儀表板示意。頁面被瀏覽器解析出主要導覽、平台 tab、LINE 流程與 FAQ 互動控制。

畫面觀察：深鈷藍 Hero 與白色儀表板形成清楚對比；CTA 與 dashboard 均在首屏可見；底部列出「100 所為展示數據」與正式名稱／網址待確認，沒有把展示數字表述成正式營運成果。

待完成：平台 tab、FAQ、語言切換與手機版互動驗證；完成後把結果補到本文件。

第二次瀏覽器操作：頁面仍可正常載入並在平台區段顯示主要 metrics、校點活動摘要與流程健康度；瀏覽器元素索引可辨識 6 個平台 tab。第一次以元素索引點擊校點管理後，畫面仍顯示總覽，需改用座標或重新取得狀態確認事件是否觸發。

第三、四次瀏覽器操作：FAQ 點擊驗證通過，畫面自動捲至 FAQ 並展開「100 所學校是真實服務範圍嗎？」；其餘問題保持收合。平台 tab 的元素索引點擊仍未在畫面上反映切換，下一步將先直接定位 `#platform` 再測試。

第五、六次瀏覽器操作：先定位 `#platform` 後點擊「校點管理」，平台 tab 互動驗證通過。畫面由「營運總覽」切換為「校點管理」，顯示基隆、台北、新北、桃園展示校群與 100 所啟用檢核，並保留正式資料邊界提醒。

第七、八次瀏覽器操作：語言下拉選單切換至英文後，導覽與 Hero 文案即時切換為英文；再切回繁體中文後恢復原文案。語言偏好使用 localStorage 保存；平台內容主體維持繁中展示資料，作為本版語言預覽邊界。

Cloudflare Pages Preview：PR #10 的 Pages check 為 SUCCESS。已驗證以下兩個網址均回應 HTTP 200、HTML 內容大小 70,602 bytes，頁面標題與「校鮮集」內容正確：

- Commit Preview：`https://1593eafd.stallpay-lp.pages.dev`
- Branch Preview：`https://feat-xiaoxianji-enterprise-p.stallpay-lp.pages.dev`

同一 PR 的既有 `Workers Builds: stallpay-landing` check 為 FAILURE；此 check 與本次 Pages Preview 是分開的部署管線，Cloudflare Pages 本身已成功。正式 Workers build 的失敗原因需由 Cloudflare 專案 owner 於 dashboard 進一步查看；本次未更動該 Workers 設定。

2026-09-09 更新驗證：新增 `#coop-line` 個別合作社 LINE 整合展示。瀏覽器確認首屏可見合作社情境選擇器、教職員工／在校學生切換、LINE 手機對話，以及 Order AI、Loop、StallPay 三張互動流程卡。

互動驗證通過：
- 預設「北區員生合作社／教職員工」顯示團購、訂單與取貨對話。
- 點擊「校園員生合作社」後，標題、LINE 對話、選單與資料邊界更新。
- 再點擊「在校學生」後，更新為學生餐點／用品／取貨情境，並保留正式付款與身分驗證待確認提示。
- 3 個合作社情境與 2 個服務對象皆由同一組前端狀態互動切換；未連接外部 API。

第三個情境驗證：切換至「單位福利合作社」後，畫面正確更新為學生福利資格詢問、人工資格判定與合作社邊界提示。網站版本同步更新為 `Prototype v0.2｜2026-09-09`。

2026-09-09 v0.3 更新驗證：以版本查詢參數重新載入本機頁面，確認首頁導覽新增「ERP 儀表板」，平台管理台新增「多校庫存」tab，且 ERP 管理入口可見財務對帳與多校庫存兩張摘要卡。

多校庫存互動驗證通過：點擊「查看多校庫存畫面」會切換平台至「多校庫存儀表板」；取貨方式可切換「校內取貨」、「智販機」與「取物櫃」，說明文字分別更新為窗口核對、QR／取貨編號開櫃、一次性取貨碼開櫃的展示概念，並保留正式設備與責任 owner 待確認提示。

ERP 財務驗證通過：平台 tab「對帳中心」已更新為「ERP 財務對帳」，顯示合作社對帳批次、應收金額、已收款、待核對、異常筆數、Fail-closed 財務控制與異常人工核對提示。

Order AI 驗證通過：頁面文字與畫面內容包含教職員工低信心訊息「我想要那個乳品，週三新店拿，還有上次的米」、信心分數 0.54、商品／校點歧義、停止建單、保留草稿、轉合作社窗口與四步人工介入流程。稽核紀錄區包含 company_id、coop_id、member_id masked 與 UTC event time 展示欄位。

Cloudflare v0.3 部署證據：commit `4bb0887e996639f682a4e530ed0f9284d77f6ab3` 的 Pages Deploy successful，Commit Preview 為 `https://3e722b51.stallpay-lp.pages.dev`，Branch Preview 為 `https://feat-xiaoxianji-enterprise-p.stallpay-lp.pages.dev`。Branch Preview 回應 HTTP 200、頁面大小 105681 bytes，並確認包含 ERP 財務對帳、多校庫存、取物櫃與 Order AI review queue 內容。

同一 PR 的 `Workers Builds: stallpay-landing` 檢查於本次 commit 顯示 failure，Cloudflare 回報的部署 build ID 為 `e2d18fc4-9506-42aa-98a5-d4fbf11336cc`，無 annotations；該檢查屬既有 Workers service，與成功的 Cloudflare Pages 靜態展示 Preview 分開。Pages Preview 可作為本次對外展示入口。

2026-09-09 v0.4 本機驗證：`http://127.0.0.1:8093/?v=04b#success-flow` 可載入，導覽新增「成功資料流」與「設備模擬」。頁面文字確認成功資料流包含訂單 #OA-2048、Order AI confidence 0.96、庫存預留、庫存數量扣減、取貨批次與 ERP 批次對帳；設備模擬包含 iMin Falcon 1／F1、智販機與取物櫃三種選項。

點擊「播放完整資料流」互動可開始播放；瀏覽器在播放中畫面已由第 1 階段更新到第 2／6 階段，事件串流同步由 `order.ai.confirmed` 更新為 `order.created`，並將第一階段標示為已完成、第二階段標示為目前事件。後續將以等待後的頁面快照確認完整 6 階段與設備操作回寫。

iMin 公開資料查核：官方產品頁將型號列為 Falcon 1；官方公開資訊包含 80mm 熱感印表機、QR／1D／2D 掃描、NFC、Android 11、Wi-Fi、Bluetooth、4G、GPS 與多種連接埠。SDK／Printer 文件已保存於 `IMIN_F1_RESEARCH.md`，原型只將其作為候選設備 Adapter，不宣稱正式接通。

設備模擬互動驗證進度：點擊「iMin Falcon 1／F1」後，畫面切換至 iMin Falcon 1 取貨終端；點擊「掃描 QR／取貨碼」後，設備事件由 `device.ready` 進入 `pickup.verify`，畫面更新為「訂單已核對」、主要按鈕更新為「完成取貨」，並標示第一事件已完成、第二事件目前處理。
成功資料流播放等待後已完成至第 6 階段：事件串流顯示 `reconcile.batch.opened`、庫存扣減 `已扣減 -2`、取貨批次 `B-20260909-07`、對帳狀態 `已建立`。

設備模擬完成驗證：再點擊「完成取貨」與「模擬狀態回寫」後，畫面依序顯示 `pickup.complete` 與 `audit.append`；最終 iMin F1 畫面顯示「狀態已回寫」、PICKED_UP，設備事件 01–04 全部顯示已完成，主要按鈕變為「已完成」並停用，符合模擬失敗不標記完成的邊界說明。

設備選項覆核：切換「智販機」後，畫面標題變為「智販機取貨終端」、按鈕變為「掃描 QR／模擬設備檢查」，事件標籤更新為 QR 掃描／格位取貨；切換「取物櫃」後，畫面標題變為「取物櫃取貨終端」、按鈕變為「輸入取貨碼／模擬設備檢查」，事件標籤更新為取貨碼輸入／取物櫃開啟。三種設備均共用 Adapter 事件回寫展示模型。

Cloudflare v0.4 部署證據：commit `706d071f6e61c68c6a98edb7b4d7cea1082e2adb` 的 Cloudflare Pages check 為 SUCCESS。Commit Preview：`https://7714fcd7.stallpay-lp.pages.dev`；Branch Preview：`https://feat-xiaoxianji-enterprise-p.stallpay-lp.pages.dev`。兩個網址均已驗證 HTTP 200、回應大小 133849 bytes；Branch Preview 內容包含 `Prototype v0.4`、成功資料流標題、`iMin Falcon 1／F1` 與「智販機與取物櫃」。

同一 PR 的既有 `Workers Builds: stallpay-landing` check 為 FAILURE，Cloudflare Pages 不受影響且已成功提供 Preview。Workers Build failure 沒有 GitHub annotations，Cloudflare bot 只提供 build log 連結；目前不將該獨立 Workers 管線失敗描述為本次 Pages 原型失敗。Workers log：https://dash.cloudflare.com/963e5bb95f818c9901c6be84ce681b3e/workers/services/view/stallpay-landing/production/builds/855ff8f3-ebc1-446f-b9d5-a002c6ee2988

2026-09-09 v0.5 本機驗證：`http://127.0.0.1:8094/?v=05#benefit-settlement` 可載入，導覽新增「福利結算」、「iMin 收銀」、「設備通知」。頁面文字與畫面確認福利、收銀、異常通知三個新模組均已渲染。

點擊「執行自動結算」後，福利批次已開始播放：畫面由待執行更新至處理中 1/4，再到 2/4；第一階段 `benefit.source.orders` 顯示已完成，第二階段 `benefit.points.calculated` 顯示目前，會員狀態同步由待結算更新為已計算，表示結算互動可正常更新資料表與右側帳本。

 iMin F1 收銀互動驗證通過：在團購發票模式先點擊「確認金額」，畫面進入「金額已確認／準備列印」，顯示 `cashier.total.confirmed`；再次點擊主要按鈕後，畫面顯示「收銀事件已回寫」、發票樣張產生 `AB-20260909-2048`、狀態為「發票已列印／已回寫」，並顯示 `printer.invoice.printed`。正式付款、發票與稅務仍保留待確認邊界。

設備異常通知互動驗證進行中：定位 `#device-alerts` 後點擊「觸發 LINE 通知流程」，畫面由待觸發更新至處理中 2/4；`device.alert.received` 與 `restock.task.created` 已完成，`line.notification.queued` 顯示目前，LINE 手機畫面同步顯示 VM-07 低庫存與補貨任務 RT-0709。流程設計為最後寫入稽核紀錄並維持人工確認。

頁尾新增：`製作／服務提供者：捷州資訊`。

設備異常通知最終驗證通過：播放完成後，LINE 手機畫面顯示「請管理者確認任務，系統不自動關閉異常」；右側四個事件 `device.alert.received`、`restock.task.created`、`line.notification.queued`、`audit.log.appended` 全部顯示已完成，狀態為「已通知・待確認」，事件碼標示 `waiting_human_ack` 與 `fail_closed: true`。

Cloudflare v0.5 部署證據：commit `6c6715d2e48075ad33f46a7dcf50dc16592f7945` 的 Cloudflare Pages check 為 SUCCESS，Cloudflare bot 回報 Commit Preview `https://70063c61.stallpay-lp.pages.dev`、Branch Preview `https://feat-xiaoxianji-enterprise-p.stallpay-lp.pages.dev`。Branch Preview 已以 curl 驗證 HTTP 200、內容包含 Prototype v0.5、福利點數與回饋金、iMin F1 收銀、設備庫存異常與捷州資訊。

同一 PR 的 `Workers Builds: stallpay-landing` check 為 FAILURE，為既有 Workers pipeline／服務的獨立檢查；不影響本次 Cloudflare Pages 靜態 Preview 成功。Cloudflare Workers 建置紀錄：https://dash.cloudflare.com/?to=/963e5bb95f818c9901c6be84ce681b3e/workers/services/view/stallpay-landing/production/builds/5b7b3f24-65e0-48b8-aeb2-524a5bc62a82

2026-09-09 v0.6 頁尾驗證：頁尾新增獨立高可見度區塊「本展示網站製作／服務提供者｜捷州資訊」，使用金色左框與高對比文字呈現；版本標記更新為 `Prototype v0.6｜2026-09-09`。以本機 `http://127.0.0.1:8095/?v=06#faq` 開啟並定位頁尾，瀏覽器畫面與文字抽取均確認捷州資訊可見。

2026-09-09 公開頁尾再次檢查：以 `https://feat-xiaoxianji-enterprise-p.stallpay-lp.pages.dev/?v=06#faq` 開啟公開 Branch Preview，瀏覽器實際畫面定位至頁尾，確認可見「本展示網站製作／服務提供者｜捷州資訊」。curl 回應 HTTP 200、174169 bytes，並確認 HTML 包含 `Prototype v0.6`、`製作／服務提供者：捷州資訊` 與 `<strong>捷州資訊</strong>`。

2026-09-09 新增操作文件：`IMIN_F1_AND_SETTLEMENT_OPERATIONS.md`，涵蓋 iMin F1 三種收銀模式、確認金額／列印／重置步驟、四階段福利自動結算、事件名稱、異常處理、Adapter 邊界與正式實作前待確認事項。

2026-09-09 v0.7 圖一格式更新：頁尾由原「服務提供者」卡片改為深綠色單行主權展示列，內容為 `© 2026 JCINN 捷州資訊. Concept showcase.`，並列出 `§1 平台中立 · §2 原始碼主權 · §3 標準化部署 · §4 技術棧白名單 · §5 資料主權 · §6 AI 可替換 · §7 主權檢核`。原型版本標記更新為 `XIAOXIANJI-V0.7`；舊的金色服務提供者卡片已移除。待本次 commit 部署後，需再次以公開網址核對。

2026-09-09 v0.7 本機瀏覽器驗證：以 `http://127.0.0.1:8096/?v=07#faq` 開啟後，頁尾實際呈現 `© 2026 JCINN 捷州資訊. Concept showcase.`，同一行接續 §1 至 §7 主權條款；畫面背景為深綠色、上方有細分隔線，與圖一格式一致。舊的「製作／服務提供者」金色卡片已不再呈現。

2026-09-09 v0.7 三溫層異常補救模組初次驗證：以 `http://127.0.0.1:8097/?v=07-remediation#thermal-remediation` 開啟頁面，瀏覽器可辨識新增「異常補救」導覽、3 個溫層選項、4 個異常情境、播放／人工確認／重置控制。常溫／開門失敗初始顯示 `OPEN_FAILED`、AMBIENT-01、A-12、訂單 #OA-2048；點擊「播放補救流程」後畫面由異常偵測進入 fail-closed／人工任務流程，顯示禁止自動重試、預留保留與事件串流。

本次新增展示邊界已確認：頁面文字明確說明不會實際開門、發送 LINE、修改庫存或完成正式訂單；補救完成需另外點擊「模擬人工確認」。

2026-09-09 v0.7 異常補救流程互動驗證：常溫／開門失敗播放完成後，畫面停在 `HUMAN REVIEW・待確認`；事件 01–04 已完成、05 `human.review.required` 為目前，`OPEN_FAILED`、預留保留、禁止自動重試與「已排入展示佇列」均正確顯示。按下「模擬人工確認」後，畫面更新為 `AUDIT LOGGED・展示完成`、狀態「補救展示已留痕」，事件 01–06 全部完成，`audit.log.appended` 與 `fail_closed: true` 可見；按鈕變成「已完成人工確認」。此結果只代表展示稽核流程完成，不代表正式設備或訂單完成。

2026-09-09 v0.7 溫層分支驗證：切換「加熱／保溫」後設備與格位更新為 `HEAT-01`／`H-03`，再切換「溫層條件不明」後異常代碼更新為 `TEMPERATURE_UNKNOWN`，畫面顯示「溫層待人工確認」、暫停交付與禁止自動重新加熱／開門的展示邊界；切換情境會重設播放狀態。

2026-09-09 v0.7 冷藏／物品未取出分支驗證：切換「冷藏」後設備與格位更新為 `COLD-01`／`C-07`；切換「物品未取出」後異常代碼為 `ITEM_NOT_RETRIEVED`，畫面顯示「門已開不等於商品已取出」、庫存轉入實體盤點待核對與禁止重複開門。三種溫層皆可搭配異常情境切換。

2026-09-09 v0.7 開門結果不明分支驗證：切換後異常代碼為 `OPEN_RESULT_UNKNOWN`，畫面顯示「狀態待確認」、無法確認設備是否收到指令、禁止再次開門與等待設備查詢／人工處理的路徑，符合結果不明時不重試的 fail-closed 原則。

2026-09-09 v0.7 重置驗證：點擊「重置異常展示」後，開門結果不明情境回到 `EXCEPTION MOCK・待播放`，事件回到異常偵測目前、其他節點待處理；目前選取的溫層／異常保留，播放進度清除，符合可重播展示控制。

2026-09-09 v0.7 三溫層異常補救部署證據：commit `3e7060d943d739f1c46ddfd483a3fdd46f178e16` 的 Cloudflare Pages check 為 SUCCESS；Branch Preview `https://feat-xiaoxianji-enterprise-p.stallpay-lp.pages.dev/?v=07-remediation` 回應 HTTP 200、內容大小 196567 bytes，並確認包含 `Thermal pickup exception remediation`、`OPEN_RESULT_UNKNOWN`、`XIAOXIANJI-V0.7` 與 `© 2026 JCINN 捷州資訊`。Cloudflare Pages build metadata 顯示 `mode=DEMO_MOCK`、`formal_connections=false`、`formal_device_control=false`、`formal_inventory_write=false`、`real_api_query_count=0`；本次仍為靜態展示，不連接正式設備或資料服務。
