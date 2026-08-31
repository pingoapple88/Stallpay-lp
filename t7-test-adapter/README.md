# StallPay T7 唯讀網路 Preflight Adapter

## 目的

此服務提供 `go.stall.merchcore.ai/t7-test` 的受控網路檢查。它只允許查詢天來 API 文件中的 `Machine.aspx` 與 `Commodity.aspx`，用於驗證 DNS、HTTPS、伺服器時間、延遲、憑證設定與唯讀 API 回應。此服務不提供開門、鎖貨、出貨、預訂、庫存寫入、退款或自動重送。

## 資料與憑證邊界

初始 `TIANLAI_COMPANY`、`TIANLAI_TOKEN`、`T7_TESTER_ACCESS_KEY`、`T7_MANAGER_ACCESS_KEY` 與 `CREDENTIAL_ENCRYPTION_KEY` 只能由 Railway 環境變數提供。`company=2000162` 可作為 bootstrap 預設；目前 sample 只含不可逆的 `sign`，無法安全還原 token，因此部署時可讓 `TIANLAI_TOKEN` 保持空值，由持有主管管理碼的 `SUPER_ADMIN` 在網頁輸入 token 建立第一個加密版本。之後也只有 `SUPER_ADMIN` 能建立新版本或回滾。

一般現場工程師只提交測試授權碼並執行唯讀 preflight，不能讀取或修改 company／token。天來 token 不傳送到一般測試流程、不寫入 Git、不寫入 log、不寫入 response，也不進入 JSON／CSV 匯出。主管在 TLS 頁面單次輸入 token 後，瀏覽器立即清空欄位；正式執行若缺少 active token、測試授權碼、主管管理碼、加密金鑰或資料庫連線，preflight 必須回傳 blocked，不得降級成公開外連。

## API Contract

| Route | Method | 用途 | 驗權 |
|---|---|---|---|
| `/healthz` | `GET` | Adapter 健康狀態與憑證是否已設定；不回傳憑證值 | 無；不執行外連 |
| `/api/v1/t7/network/preflight` | `POST` | 執行 DNS、HTTPS、時間差及 `Machine.aspx`／`Commodity.aspx` 唯讀查詢 | `X-T7-Test-Key`；`TESTER` 以上 |
| `/api/v1/t7/settings/status` | `GET` | 回傳設定版本、來源及遮罩狀態，永不回傳 token | `X-T7-Manager-Key`；`SUPER_ADMIN` |
| `/api/v1/t7/settings` | `PUT` | 新增 company／token 設定版本並切換為 active | `X-T7-Manager-Key`；`SUPER_ADMIN` |
| `/api/v1/t7/settings/rollback` | `POST` | 回滾至指定既有版本 | `X-T7-Manager-Key`；`SUPER_ADMIN` |

Request body：

```json
{
  "run_id": "T7-WEB-20260831T000000Z",
  "client_time_utc": "2026-08-31T00:00:00Z",
  "device_role": "cargo_lane_machine",
  "device_id": "test-device-001",
  "site_label": "Tianlai field test"
}
```

Response 僅包含狀態、UTC、時間差、DNS／HTTPS 結果、HTTP status、耗時、回應大小、SHA-256、頂層欄位名稱、collection 名稱與筆數。不得包含完整 request URL、query string、company、token、sign、設備清單、商品內容或 raw response body。

## 簽章規則

依附件 API 文件第 4 頁，所有參數名依 ASCII 由小至大排序，以 URL Query String `key=value&key=value` 格式串接，在字串尾端直接接上 token，再進行 SHA-256。`sign` 本身不參與簽章。文件範例 `MerchantID=0001&OrderID=0123456TEST` 可重現文件所列 SHA-256。

## 主管權限、加密與稽核

授權層透過 `IAuthorizationProvider` 抽象；第一版使用 Railway ENV 中的兩把獨立 access key，映射為 `SUPER_ADMIN` 與 `TESTER`。每個受保護 route 進入後先驗權，再執行任何資料庫或 upstream 操作。

company／token 使用 Fernet authenticated encryption 保存於 PostgreSQL；每次變更建立不可變版本，只有一筆 active。`audit_logs` 保存 UTC、actor hash、action、設定版本與前後 fingerprint，不保存 company／token 明文。回滾是建立指向既有加密版本的新 active 版本，不覆寫歷史。

## 安全限制

允許的 upstream host 固定為 `api.tenlifeservice.com`，允許 path 固定為 `/Machine.aspx` 與 `/Commodity.aspx`，HTTP method 固定為 `GET`，禁止 redirect。請求逾時採 connect 5 秒、read 15 秒。所有結果 fail-closed；upstream 連線成功不會改變 `GATE-06=BLOCKED` 或 `TEST_DEVICE_VERIFIED=false`。

此服務只使用 PostgreSQL 保存加密 integration credential 版本與 audit log，不保存機台清單、商品內容或現場測試結果。若未來要集中保存測試結果，必須另開資料 owner、RBAC、company scope、PII／audit 與 migration 審核。
