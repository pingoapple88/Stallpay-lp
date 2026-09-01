# 天來 API v2.7 文件核對與唯讀 Request Contract

| 欄位 | 核對結果 |
|---|---|
| Work Order | `WO-T7-W2-P1` |
| 執行模式 | `READ_ONLY_DISCOVERY + SYNTHETIC_FAULT_HARNESS` |
| 核對日期 | 2026-09-01 |
| 交付狀態 | `BLOCKED_BY_ENDPOINT_SCHEMA` |
| 真實 API 查詢 | 未執行 |
| 正式 Token／正式資料 | 未使用 |

> **版本判定：**目前取得的 PDF 建立日期為 2025-12-09，共 24 頁，但 PDF 內未找到 `v2.7` 或「第 10 節」標記；共享問答文件則明確稱現有文件為 `v2.5`。因此不能把現有材料認定為 Work Order 指定的 v2.7 第 10 節權威文件。[1]

## 一、文件核對表

| 核對項目 | 目前證據 | 判定 |
|---|---|---|
| v2.7 版本號 | 現有 PDF 無 `v2.7` 文字標記 | `[TODO: 待人工確認]` |
| 第 10 節 | 現有 PDF 無「第 10 節」可識別標記 | `[TODO: 待人工確認]` |
| 文件日期 | PDF metadata：2025-12-09 | `OBSERVED_NOT_VERSION_CONFIRMED` |
| 文件來源 | 使用者提供供應商 PDF；SHA-256=`76da3e56811c37be228639b8a8646cc6bb8398805571cf55cfd1739e07e4ce5a` | `RECEIVED` |
| 正式 request 範例 | 現有 PDF 含部分 URL、參數與回應範例，但不構成 v2.7 第 10 節證明 | `PARTIAL／UNCONFIRMED_VERSION` |
| Base URL 分類 | 現有材料出現 `api.tenlifeservice.com` 與 `www.tenlifeservice.com`；sandbox／test／production 分類未確認 | `[TODO: 待人工確認]` |
| Executing owner | 未指定 | `[TODO: 待人工確認]` |
| Company scope | 專屬 customer code 曾獲使用者確認，但 Work Order 所要求的受控執行 scope 未重新核准 | `[TODO: 待人工確認]` |
| 測試 Token | 雲端 Adapter health 顯示尚未設定；不得從 sample sign 反推 | `UNSET／BLOCKED` |

## 二、來源衝突與可重用資產

| 項目 | 現況 | T2 可採用方式 |
|---|---|---|
| `Machine.aspx` | 既有 client 使用 GET，query 為 `company`＋`sign` | 只能作候選 contract；待 v2.7 owner 核准 |
| `Commodity.aspx` | 既有 client 使用 GET，`commodityCode`／`commodityID` 選填，另有 `company`＋`sign` | 只能作候選 contract；待 v2.7 owner 核准 |
| `MachineCommodity.aspx` | 既有 client 使用 GET，`code`＋`company`＋`sign`；現有 2025-12-09 PDF 文字則列 `RestockCommodity.aspx`／`OrderMachineCommodity.aspx`，未直接證實 Work Order 指定名稱 | `BLOCKED_BY_ENDPOINT_SCHEMA`；fixture 僅可標 synthetic |
| `IVendingMachineProvider` | 目前只定義 `getProducts`、`getSales`、`getStatus`、`pushAd`、`setCoupon` | 不得宣稱已有 machine↔commodity canonical mapping contract |
| `TenlifeVendingProvider.getProducts` | 現況回空陣列，註解仍稱沒有 Commodity endpoint | T2 需要以核准欄位修正；T7 只交 canonical input，不代改 core |

## 三、候選 Request Contract

以下內容只反映既有 client 與未確認版本的材料；在 v2.7 owner 核准前，`documented_http_method` 一律視為候選，不得用於真實查詢。[1] [2]

### 3.1 Machine.aspx

| 欄位 | 值 |
|---|---|
| Endpoint | `/Machine.aspx` |
| Candidate HTTP method | `GET` |
| Required query | `company`、`sign` |
| Optional query | `[TODO: 待人工確認]` |
| Headers | 一般 HTTPS request；額外 Header `[TODO: 待人工確認]` |
| Signature | 候選規則：參數名 ASCII 升冪、排除既有 `sign`、串接 TokenKey 後 SHA-256 lowercase hex；正式大小寫／時效／防重播規則 `[TODO]` |
| Pagination／date limit | `[TODO: 待人工確認]` |
| Candidate response | `state`、`message`、`machine[]` |
| Candidate machine fields | `code`、`user`、`name`、`qty`、`module1`～`module6` |
| Scope rule | 回傳 machine 必須屬於 server principal 的 company；不一致 fail-closed |

### 3.2 Commodity.aspx

| 欄位 | 值 |
|---|---|
| Endpoint | `/Commodity.aspx` |
| Candidate HTTP method | `GET` |
| Required query | `company`、`sign` |
| Optional query | `commodityCode`、`commodityID` |
| Headers | 一般 HTTPS request；額外 Header `[TODO: 待人工確認]` |
| Signature | 同 3.1；正式規則 `[TODO: 待人工確認]` |
| Pagination／date limit | `[TODO: 待人工確認]` |
| Candidate response | `state`、`message`、`commodity[]` |
| Candidate core fields | `commodityID`、`commodityCode`、`commodityName`、`price`、`stop` |
| Candidate optional fields | `commodityName2`、type、brand、spec、info、memo、url、photo、bigPhoto、index、clear、vip |
| Money rule | 天來候選原生單位為整數「元」；T2 Adapter 對核心輸出時轉 integer minor units（×100） |
| Scope rule | 商品資料只能在核准 company／machine mapping 範圍內供可操作流程消費 |

### 3.3 MachineCommodity.aspx

| 欄位 | 值 |
|---|---|
| Endpoint | `/MachineCommodity.aspx` |
| Candidate HTTP method | `GET`，僅來自既有 client；v2.7 權威文件未取得 |
| Required query | 候選：`code`、`company`、`sign` |
| Optional query | `[TODO: 待人工確認]` |
| Headers | `[TODO: 待人工確認]` |
| Signature | 候選同 3.1；正式規則 `[TODO: 待人工確認]` |
| Pagination／date limit | `[TODO: 待人工確認]` |
| Candidate response | `state`、`message`、`commodity[]` |
| Candidate mapping fields | `layer`、`commodityID`、`commodityCode`、`shelflife` |
| Machine identity | 候選由 request `code` 帶入；response 是否重覆回 machine code `[TODO]` |
| Slot／layer format | `[TODO: 待人工確認]`；不得假設 `A01`、`AB3` 等格式為所有機型通則 |
| Scope rule | `machine_code + commodity_code + layer` 必須同時落在核准 company；任一不一致即 blocked |

## 四、正式探索前置條件

| Gate | 必要證據 | 目前狀態 |
|---|---|---|
| Owner | executing owner／API owner 書面核准 | `BLOCKED_BY_OWNER` |
| Document | v2.7 第 10 節原檔、日期與 request sample 位置 | `BLOCKED_BY_ENDPOINT_SCHEMA` |
| Environment | Base URL 的 sandbox／test-device／production 分類 | `BLOCKED_BY_OWNER` |
| Scope | company、machine、commodity 查詢邊界 | `BLOCKED_BY_OWNER` |
| Credential | 受控環境變數注入，不得寫入 Git／log／URL | `UNSET` |
| Execution | 每端點最多一個最小唯讀 query，不重試、不改參數 | `NOT_EXECUTED` |

因多項 Gate 未解除，本輪只建立 synthetic fixtures、fault matrix 與 T2 readback。真實 API 執行狀態必須維持 `BLOCKED_BY_ENDPOINT_SCHEMA`，不得標示 `READ_ONLY_DISCOVERY_COMPLETE`。

## References

[1]: ./source_inventory.md "WO-T7-W2-P1 去敏來源清冊"
[2]: https://github.com/pingoapple88/stallpay-v2/blob/f883fa9e617b41e8e0885ad821975f56bb6ae99f/server/vending/providers/tenlife/tenlifeClient.ts "既有 Tenlife client 候選 contract"
