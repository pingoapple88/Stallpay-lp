# T7 正式測試網址部署證據

## 部署資訊

- Target：`https://go.stall.merchcore.ai/t7-test`
- Effective URL：`https://go.stall.merchcore.ai/t7-test/`
- Repository：`pingoapple88/Stallpay-lp`
- Branch：`feat/t7-web-test-mode`／production `main`
- Published HEAD：`6105145efca0f5d807ac108823b0a57dcf7054c5`
- Parent／rollback：`daed051393497d141d9790f81e06c5ee2e29f81e`
- HTTPS verification UTC：`2026-08-31T13:34:29Z`

## HTTP 與 Browser Readback

正式入口先回傳 HTTP `308` 至 `/t7-test/`，追蹤後回傳 HTTP `200`。頁面標題為 `StallPay｜天來無人銷售測試模式`，可見 `DEMO_MOCK／測試資料`、QR／門鎖／鎖貨／取貨／機台回報、自助式測試設定、12 種情境、JSON／CSV 匯出、`completion_signal=false` 與 `GATE-06=BLOCKED`。

正式頁面已在 browser 儲存預設自助設定：batch=`天來現場無人銷售測試`、owner=`Dennis`、device=`demo-device-001`、store=`demo-store`、mode=`DEMO_MOCK`。這些資料為 synthetic；未輸入 customer code、token、sign、密碼或正式設備憑證。

既有首頁 `https://go.stall.merchcore.ai/` 回傳 HTTP `200`，仍可辨識 StallPay 首頁內容。

## 當前邊界

目前只驗證正式網址的 browser simulator。頁面沒有正式 API call、設備控制、server／database persistence、正式庫存寫入、退款或 unknown 自動重送。`TEST_DEVICE_VERIFIED=false`。

## 正式網址完整套件驗證

Browser UTC：`2026-08-31T13:35:41Z`。正式頁面執行完整 12 情境套件成功，產出總數 `12`、PASS=`2`、ATTENTION=`5`、BLOCKED=`5`。正常流程為 `QR_SCAN → ACCESS_VERIFIED → DOOR_OPEN → GOODS_LOCKED → PICKUP_DISPENSED → DOOR_CLOSED → MACHINE_REPORTED`；其餘 QR 失敗／過期、門鎖阻擋／未知、鎖貨衝突、取貨未知、庫存不足、離線、溫度需注意、卡貨及固定資訊回報皆顯示預期狀態與 fail-closed 結果。

正式頁面的去敏 JSON 匯出已成功觸發，頁面提示不包含 customer code、token、sign 或密碼。`completion_signal=false`、`GATE-06=BLOCKED`、`TEST_DEVICE_VERIFIED=false` 保持不變。

正式 browser 截圖：`/home/ubuntu/screenshots/go_stall_merchcore_a_2026-08-31_13-35-42_8085.webp`、`/home/ubuntu/screenshots/go_stall_merchcore_a_2026-08-31_13-35-57_6558.webp`。

## 正式頁面 Session 與 CSV 驗證

正式頁面 CSV 匯出按鈕已成功觸發，頁面提示不包含 customer code、token、sign 或密碼。瀏覽器執行環境內直接核對 `selfState` 結果：`ok=true`、output_count=`12`、PASS=`2`、ATTENTION=`5`、BLOCKED=`5`；十二個 scenario ID 完整。

全部輸出皆保持 `completion_signal=false`、`gate_06=BLOCKED`。`formal_api_called=false`、`formal_device_control=false`、`formal_inventory_write=false`、`direct_refund=false`、`unknown_auto_resend=false`；customer code marker=`REDACTED_NOT_EXPORTED`、data mode=`DEMO_MOCK`。

瀏覽器下載檔案未映射至 sandbox 的 `/home/ubuntu/Downloads`，因此 production 匯出內容採頁面 session 物件與畫面提示驗證；repository 內仍保留本地 browser smoke 取得並驗證過的 12 筆 JSON／CSV sample。

正式 browser 截圖：`/home/ubuntu/screenshots/go_stall_merchcore_a_2026-08-31_13-36-26_2133.webp`。Console evidence：`/home/ubuntu/console_outputs/exec_result_2026-08-31_13-38-31_750.txt`。
