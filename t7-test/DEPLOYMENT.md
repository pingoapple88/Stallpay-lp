# T7 自助測試頁部署說明

## 目標

正式測試入口固定為 `https://go.stall.merchcore.ai/t7-test`。既有網域目前由 Cloudflare 提供 HTTPS，DNS 解析至 `stallpay-lp.pages.dev`；原始碼 repository 為 `pingoapple88/Stallpay-lp`，預設分支 `main`。準備部署時的 `main` 基線為 `daed051393497d141d9790f81e06c5ee2e29f81e`。

在本次變更前，`/t7-test` 回傳 HTTP 200，但畫面仍是 StallPay landing page，表示該路徑尚未提供 T7 測試內容。此變更只新增 `t7-test/` 靜態目錄，不修改既有首頁、方案、表單、付款、登入、資料庫或正式設備流程。

## 部署方式

Cloudflare Pages／Workers 的成品由根目錄 `wrangler.jsonc` 管理。建置時必須執行 `python3 scripts/build_cloudflare_pages.py --output dist`，再以 `dist/` 作為 static asset root；此步驟會保留既有首頁並在 `dist/t7-test/build-metadata.js` 寫入當次 Git HEAD 的 stamped provenance。不得直接把 repository 根目錄的未蓋章 `t7-test/build-metadata.js` 作為公開成品。

正式發布前必須確認：feature branch 的本地 smoke、安全掃描與路徑驗證全部通過；使用者明確確認將變更發布至正式網站；發布後再以 HTTPS 重新執行 browser smoke。若 `/t7-test` 未更新、破壞首頁或出現安全問題，立即回滾至部署前 `main` SHA。

## 安全邊界

頁面固定為 `DEMO_MOCK`／`MOCK`，`completion_signal=false`、`GATE-06=BLOCKED`。頁面不呼叫外部 API、不控制正式設備、不寫入 server／database／正式庫存、不退款、不保存 customer code／token／sign／密碼；測試輸出只存在瀏覽器 session，必須由測試人員下載 JSON／CSV 保存。

## 回滾

部署前 rollback reference：`daed051393497d141d9790f81e06c5ee2e29f81e`。如需回滾，將 production branch 還原至此 SHA 或 revert 本次 T7 deployment commit，再等待 Cloudflare Pages 完成重新發布並重測首頁與 `/t7-test`。

## 未確認事項

正式 Cloudflare Pages build／deployment owner、branch protection、production deployment hook 與 `go.stall.merchcore.ai` routing owner 仍為 `[TODO: 待人工確認]`。目前 repository 已提供 `wrangler.jsonc` build command 與 `scripts/build_cloudflare_pages.py`；部署 owner 仍須在 Cloudflare Pages 專案確認 Build command 為該命令、Output directory 為 `dist`，再進行發布。

## 正式發布紀錄（2026-08-31）

- 發布狀態：`DEPLOYED_SIMULATOR_ONLY`
- 正式網址：`https://go.stall.merchcore.ai/t7-test`
- Effective URL：`https://go.stall.merchcore.ai/t7-test/`
- Hosting：Cloudflare Pages
- Production branch：`main`
- Published source commit：`6105145efca0f5d807ac108823b0a57dcf7054c5`
- Parent／rollback：`daed051393497d141d9790f81e06c5ee2e29f81e`
- HTTPS：PASS；requested path HTTP `308`，effective path HTTP `200`
- Existing homepage：HTTP `200`
- Browser smoke：12 scenarios；PASS=`2`、ATTENTION=`5`、BLOCKED=`5`
- JSON／CSV export controls：PASS
- Safety：`completion_signal=false`、`GATE-06=BLOCKED`、`TEST_DEVICE_VERIFIED=false`

回滾方式：將 `main` 還原至 `daed051393497d141d9790f81e06c5ee2e29f81e`，或反轉 `6105145efca0f5d807ac108823b0a57dcf7054c5` 中的 `t7-test/` 路徑。
