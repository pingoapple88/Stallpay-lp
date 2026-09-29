# 校鮮集第一階段人工覆核與 OrderAI 狀態流程規格草案

**文件性質：**校鮮集專案專屬規格草案，不是正式開發規格或外部服務整合核准書  
**文件版本：**v0.1  
**日期：**2026-09-28  
**適用範圍：**第一階段 synthetic fixture、mock／blocked／isolated UAT 及人工覆核流程  
**正式資料、正式 ERP、正式付款、正式發票、正式稅務與正式設備控制：**均為 `[TODO: 待人工確認]`

## 1. 目的與邊界

本文件定義校鮮集從來源訊息到人工確認、ERP 待確認資料與 synthetic UAT 的最小流程。第一階段只驗證：

- 校鮮集自己的來源事件、解析草稿、人工覆核與狀態歷程。
- OrderAI 解析結果如何在低信心、缺欄位、商品不明、校點不明或 PII 邊界失敗時停止自動處理。
- 校鮮集如何將已確認草稿轉換為 provider-neutral ERP 待確認意圖。
- blocked／mock／isolated UAT Adapter 的一致輸出、冪等與 audit evidence。
- 低信心或未知結果不得自動建正式訂單、扣庫、付款、開票、出貨或控制設備。

本文件不核准下列內容：

- 校鮮集正式產品定位、正式客戶、法人、合作社、學校或門店資料。
- 雲鼎 ERP 或捷州 ERP 的正式 endpoint、credential、商品 ID、門店 ID、正式 mapping 或正式 schema。
- 任何真實會員、LINE 使用者、電話、地址、商品、價格、訂單或財務資料。
- 正式付款、電子發票、會計入帳、稅務申報、智販機、取物櫃或三溫層設備控制。

## 2. 來源證據與採用方式

| 來源 | 版本證據 | 本草案可參考內容 | 不可直接帶入 |
|---|---|---|---|
| OrderAI Backend | `pingoapple88/orderai-backend` / `main` / `1ec667cb76e725d63f2a896077793bbd664b3ecd` | `ILLMProvider`、信心與型錄風險判定、PII redaction、LINE 事件去重、`needs_human_review`、加密草稿、受控 outbox、角色檢核 | 校鮮集正式 OrderParseResult、store／company mapping、正式閾值、正式資料、正式 endpoint |
| OrderAI Jiezhou Adapter branch | `feat/jiezhou-erp-adapter` / `e118047100f2dfe1743c9a271b373aa220c43615` | blocked provider、synthetic fake、pending-order intent、scope／mapping／timeout／unknown／idempotency 測試方法 | 正式捷州 ERP 整合；該 branch 明確沒有正式 endpoint、認證或正式契約 |
| MerchCore ERP | `pingoapple88/merchcore-platform` / `main` / `1fa6cec80227f1f76bf7e5d89abbfd77e607e51f` | `OrderDraft`、`ERPOrderCommand`、audit envelope、company／sales location／legal entity scope、profile compatibility、replay、minor units、UTC | `cloud_erp` 的 synthetic scope、SKU、UUID、正式雲鼎資料或正式寫入權限 |
| 校鮮集原型 | `pingoapple88/Stallpay-lp` / `feat/xiaoxianji-enterprise-prototype` / `825b90fa8cca0abedfff495d18063d49b9cdd634` | 既有展示中的低信心、ERP、福利、設備與三溫層概念；僅作 UI／journey 參考 | 原型數字、畫面、Cloudflare Preview 或 DEMO_MOCK 不得視為正式能力 |

**校鮮集專屬 contract、fixture、mapping 與測試必須重新建立。**共用 repository 的類別名稱或測試通過，不等於校鮮集已完成整合。

## 3. 校鮮集第一階段 canonical journey 草案

```text
SOURCE_RECEIVED
  → PARSE_DRAFT_CREATED
  → HUMAN_REVIEW_REQUIRED
  → CUSTOMER_CONFIRMATION_REQUIRED（需要時）
  → XJ_CONFIRMED
  → ERP_PENDING
  → ERP_BLOCKED／ERP_ACCEPTED（依 Adapter 結果）
  → CLOSED
```

所有正式採用的狀態名稱、狀態版本與 transition table 均需 owner 核准。以下為本階段建議候選，不代表已核准。

### 3.1 狀態定義

| 狀態 | 意義 | 可進入條件 | 可做動作 | 禁止動作 |
|---|---|---|---|---|
| `SOURCE_RECEIVED` | 收到驗證過的來源事件 reference | 驗簽、來源識別與必要 scope 可建立 | 建立最小事件帳本、產生 UTC 時間與 idempotency key | 保存未遮罩 PII；直接建正式訂單 |
| `PARSE_DRAFT_CREATED` | OrderAI 已產生解析草稿 | 解析結果通過 schema validation，無論是否高信心 | 保存加密草稿、reason codes、模型識別與決策 audit | 將草稿視為已確認訂單；直接扣庫 |
| `HUMAN_REVIEW_REQUIRED` | 需要授權人員判讀或補件 | 低信心、商品不明、數量無效、身份／校點不明、PII 失敗或模型要求覆核 | 顯示候選值、補欄位、退回、要求會員確認 | 模型自行補出商品、價格、校點或會員身份 |
| `CUSTOMER_CONFIRMATION_REQUIRED` | 需要來源會員確認草稿 | 人員已檢視且仍有需會員確認的欄位 | 發送受控確認訊息、記錄確認結果 | 未確認前排入外部 ERP、付款或發票 |
| `XJ_CONFIRMED` | 校鮮集人工與必要會員確認完成 | 所有 required fields 完整、scope 已確認、人工角色有權限 | 建立不可變更的 confirmed snapshot，產生 ERP outbox | 直接把確認視為外部 ERP 成功 |
| `ERP_PENDING` | 已進入 provider-neutral Adapter 階段 | 具備 contract、mapping、scope、audit reference 與冪等鍵 | 呼叫 `blocked`／`mock`／`isolated UAT` Adapter，保存 normalized result | 未通過 readiness gate 時呼叫正式 endpoint |
| `ERP_BLOCKED` | Adapter 或治理 gate 阻擋 | endpoint、credential、契約、mapping、scope 或權限任一缺失；或結果未知 | 保留 error code、安排人工處理、可依政策重試 | 自動重送未知結果；自動完成訂單 |
| `ERP_ACCEPTED` | synthetic／isolated UAT Adapter 回傳已接受 | 回應通過 response classification 與 idempotency 檢核 | 保存 provider-neutral reference 與 audit | 將 synthetic accepted 宣稱為正式 ERP 入庫 |
| `CLOSED` | 第一階段案例完成收斂 | 人工確認與 Adapter 結果均已記錄，且沒有待處理 exception | 查詢、匯出 evidence、保留 audit | 刪除事件或覆寫歷程 |
| `REJECTED` | 人工退回，不再自動處理 | 授權人員明確退回並填受控原因 | 保留原因、通知來源方、允許新案例重新提交 | 直接刪除原案例 |

### 3.2 Conversation state 與 delivery state 分離

狀態不得只用一個欄位混合對話、人工覆核與 ERP 送件結果。建議至少分成：

- `case_state`：來源、解析、人工、會員確認與案例生命週期。
- `delivery_state`：`NOT_READY`、`BLOCKED`、`QUEUED`、`ACCEPTED`、`FAILED`、`REPLAYED`。
- `review_state`：`NOT_REQUIRED`、`REQUIRED`、`IN_PROGRESS`、`APPROVED`、`REJECTED`。
- `customer_confirmation_state`：`NOT_REQUIRED`、`PENDING`、`CONFIRMED`、`DECLINED`、`EXPIRED`。

如此可避免把「人工已確認」誤解成「ERP 已成功」，也可避免把「門店有庫存」誤解成「商品已交付」。

## 4. OrderAI 解析草稿契約草案

正式欄位需由 owner 核准；下列是校鮮集第一階段的候選 provider-neutral shape：

```json
{
  "contract_version": "xj.order_parse_result.v0.1",
  "source_event_id": "xj-synthetic-event-0001",
  "source_channel": "line|web|pos|manual|csv",
  "company_id": 0,
  "store_id": 0,
  "sales_location_id": 0,
  "external_order_id": "xj-synthetic-order-0001",
  "currency": "TWD",
  "lines": [
    {
      "source_product_key": "xj-synthetic-product-a",
      "candidate_name": "Synthetic Product A",
      "quantity": 2,
      "unit": "pack",
      "unit_price_minor": null,
      "line_total_minor": null,
      "confidence": "0.00",
      "evidence_reference": "sha256:...",
      "mapping_status": "unknown"
    }
  ],
  "overall_confidence": "0.00",
  "needs_human_review": true,
  "reason_codes": ["catalog_item_unmatched"],
  "provider_name": "synthetic-orderai",
  "idempotency_key": "xj-parse-0001-v1",
  "created_at_utc": "2026-09-28T00:00:00Z"
}
```

### 4.1 欄位規則

- `company_id`、`store_id`、`sales_location_id` 由已驗證的 server principal／來源 binding 推導或核對，不接受未驗證前端值。
- `quantity` 必須是正整數；缺失、零、負數或無法判定時進入 `HUMAN_REVIEW_REQUIRED`。
- `unit_price_minor` 與 `line_total_minor` 使用整數最小貨幣單位；尚未由校鮮集型錄核准的價格只能為 `null`，不可猜測。
- `currency` 必須是三碼大寫代碼；校鮮集是否只允許 TWD 為 `[TODO: 待人工確認]`。
- `overall_confidence` 與每列 `confidence` 必須落在 0 至 1；實際 threshold 為 `[TODO: 待人工確認]`，不得把來源專案的 0.85 直接視為校鮮集核准值。
- `evidence_reference` 只保存遮罩或雜湊參照；原始訊息與 PII 進入加密草稿，不進入一般 audit JSON。
- `reason_codes` 為固定 allow-list；未知 code 必須 fail-closed，不得靜默忽略。
- `provider_name` 只作 provider-neutral 識別，不可把 SDK payload 直接穿透至 ERP Adapter。

### 4.2 最小 reason code allow-list 草案

```text
confidence_below_threshold
model_requested_human_review
missing_requested_item
catalog_item_unmatched
catalog_item_ambiguous
invalid_quantity
quantity_exceeds_limit
missing_buyer_name
buyer_identity_unresolved
missing_requested_for
requested_for_timezone_missing
sales_location_unmapped
company_scope_mismatch
store_scope_mismatch
erp_product_mapping_missing
erp_product_mapping_version_mismatch
pii_redaction_failed
duplicate_idempotency_key
idempotency_payload_conflict
provider_timeout
provider_unknown_response
```

reason code 的 owner、版本與前端顯示文案需另行核准；不得將原始錯誤、電話、LINE ID、token 或 endpoint 寫入 reason code。

## 5. 人工覆核規則

### 5.1 人工覆核觸發條件

符合任一條件即停止自動建單：

1. overall confidence 或任一品項 confidence 低於校鮮集核准 threshold。
2. 商品候選無法唯一對應校鮮集型錄。
3. 數量、單位、收單時間或校點不完整。
4. `company_id`、`store_id`、`sales_location_id` scope 不一致或無法驗證。
5. 會員身份只有轉傳者／內部 relay，無法判定實際買家。
6. PII redaction、加密或 HMAC 設定缺失。
7. 模型 provider 回傳 schema 外欄位、錯誤或未知結果。
8. 已存在相同 idempotency key 但 payload fingerprint 不同。
9. ERP contract、商品 mapping、legal entity 或 Adapter readiness 不完整。
10. 來源為圖片、語音或檔案，但 OCR／STT contract 尚未由校鮮集核准。

### 5.2 人工可執行動作

| 動作 | 角色要求 | 產生結果 | 不可做 |
|---|---|---|---|
| `REVIEW_EDIT_DRAFT` | `xj_order_reviewer` | 新 draft version、欄位差異、原因與 audit | 覆寫原始 draft |
| `REQUEST_CUSTOMER_CONFIRMATION` | `xj_order_reviewer` | `CUSTOMER_CONFIRMATION_REQUIRED` | 未送出確認就繼續送件 |
| `APPROVE_FOR_XJ` | `xj_order_manager` 或 owner 核准角色 | `XJ_CONFIRMED` snapshot | 未完成 required fields 或 scope 不明時核准 |
| `REJECT_CASE` | `xj_order_manager` | `REJECTED` 與受控原因 | 以刪除代替退回 |
| `RETRY_BLOCKED_ADAPTER` | 經授權整合／維運角色 | 新 attempt，沿用原 idempotency key | 對 unknown response 自動重送 |
| `MARK_MANUAL_RESOLUTION` | `xj_order_manager` | exception resolved audit | 沒有 evidence 就直接完成 |

### 5.3 權限最小化

- 一般會員只能提供來源訊息、查看自己的確認要求與回覆確認。
- `xj_order_reviewer` 只能處理指定 company／cooperative／store／sales location 範圍的草稿，不能調整方案、連線、帳務或正式設備設定。
- `xj_order_manager` 可核准、退回與要求重審，但仍不能繞過 Adapter readiness gate。
- 財務角色只可查看與匯出已核准的對帳 evidence；第一階段不賦予正式入帳權。
- 維運角色可查看錯誤碼與重試佇列，但不得讀取未遮罩 PII。
- 每支受保護 API 的第一個動作必須驗證身份、角色與資料範圍；所有查詢帶 `company_id`，並依校鮮集正式 hierarchy 加上 cooperative／store／sales location scope。

## 6. ERP Adapter 與事件邊界

### 6.1 Provider-neutral 介面草案

```text
ILLMProvider
  recognize_order(input) -> OrderParseResult

IOrderIngestAuditStore
  record_or_replay(audit_event) -> recorded|replayed|conflict

IErpIngestProvider
  submit_pending_order(intent) -> normalized_result

INotificationProvider
  send(notification_command) -> sent|replayed|blocked

IAuthProvider
  authenticate／bind_identity -> SessionUser
```

付款、發票、會計與設備在第一階段維持介面預留，不啟用正式 transport：

```text
IPaymentProvider       [TODO: 待人工確認]
IInvoiceProvider       [TODO: 待人工確認]
IAccountingProvider    [TODO: 待人工確認]
IDeviceProvider        [TODO: 待人工確認]
```

### 6.2 Adapter 進入條件

只有全部成立才可產生 provider-neutral ERP command：

- 解析 draft 通過 schema 與校鮮集人工覆核。
- 會員必要確認完成，或 owner 明確核准不需確認的來源類型。
- `company_id`、`store_id`、`sales_location_id` 與 legal entity 已由校鮮集 owner 確認。
- 校鮮集商品／SKU／ERP product mapping 已有版本與 owner。
- contract version、mapping version、scope version、idempotency key 與 audit reference 齊全。
- Adapter mode 明確為 `blocked`、`mock` 或 `isolated_uat`；缺省不得默認成正式連線。
- 外部回應只接受 allow-list 狀態；未知、格式錯誤、部分成功或 scope 漂移均進入 `ERP_BLOCKED`／人工處理。

### 6.3 第一階段不承諾的外部結果

- `ERP_ACCEPTED` 在 synthetic／isolated UAT 中只代表 Adapter 合約判定接受，不代表正式 ERP 已建立客戶、訂單、庫存、付款或發票。
- `ERP_BLOCKED` 只保存受控 error code，不保存 raw response、credential、token 或敏感 endpoint。
- `timeout` 可依校鮮集重試政策重試；`unknown`、idempotency conflict、scope mismatch 與 partial result 預設不可自動重試。
- 所有 attempt、decision、response classification 與人工處理都寫入 append-only audit。

## 7. 資料模型草案

正式表名需由 owner 與資料庫負責人核准；以下為邏輯資料域：

| 資料域 | 必要欄位 | 保護規則 |
|---|---|---|
| `xj_source_event_ledger` | `event_id`、`company_id`、`store_id`、`source_channel`、`event_fingerprint`、`occurred_at_utc`、`status` | unique event key；原文不落一般 audit |
| `xj_order_parse_drafts` | `draft_id`、`source_event_id`、`draft_version`、`payload_ciphertext`、`confidence`、`reason_codes`、`provider_name` | draft 內容加密；版本不可覆寫 |
| `xj_human_review_cases` | `case_id`、`draft_id`、`case_state`、`review_state`、`assigned_role`、`reason_codes` | 查詢帶 company／location scope |
| `xj_review_actions` | `action_id`、`case_id`、`actor_id`、`action`、`before_fingerprint`、`after_fingerprint`、`occurred_at_utc` | append-only；不可刪除原動作 |
| `xj_customer_confirmations` | `confirmation_id`、`case_id`、`channel`、`request_fingerprint`、`response`、`responded_at_utc` | 會員身份以加密／HMAC 參照 |
| `xj_erp_delivery_outbox` | `outbox_id`、`company_id`、`store_id`、`intent_ciphertext`、`idempotency_key`、`adapter_mode`、`status`、`attempt_count` | default blocked；唯一冪等鍵 |
| `xj_ai_decision_logs` | `decision_id`、`draft_id`、`provider`、`threshold`、`confidence`、`reason_codes`、`source_sha256` | 不保存原始 PII；記錄模型決策 |
| `audit_logs` | `actor_id`、`company_id`、`resource_type`、`resource_id`、`action`、`old_fingerprint`、`new_fingerprint`、`occurred_at_utc` | append-only、UTC、可重放 |

第一階段若使用既有共用 ERP 模組，必須建立校鮮集 migration 與 schema mapping；不得直接共用其他專案的正式資料庫或 migration。

## 8. 事件與通知草案

事件只傳遞 provider-neutral reference、scope、狀態與 audit reference，不傳遞未遮罩 PII：

```text
xj.order.source_received
xj.order.parse_draft_created
xj.order.human_review_required
xj.order.customer_confirmation_requested
xj.order.customer_confirmed
xj.order.confirmed
xj.erp.delivery_queued
xj.erp.delivery_blocked
xj.erp.delivery_accepted
xj.erp.delivery_replayed
xj.erp.delivery_manual_review
xj.order.closed
```

LINE 或其他通知由 `INotificationProvider` 處理。通知送達與業務狀態分離：通知失敗不得自動改寫訂單為完成；通知重送使用 notification idempotency key。

## 9. 第一階段 synthetic UAT 案例

每個案例均使用校鮮集專屬 synthetic fixture，記錄 fixture ID、contract version、source commit、adapter mode、expected／actual status、exit code、stdout／stderr 路徑、artifact SHA256 與 cleanup 結果。

| 案例 | 預期結果 |
|---|---|
| 高信心、型錄唯一命中、scope 完整 | 建立 `PARSE_DRAFT_CREATED`，仍依 owner 規則決定是否需要人工與會員確認 |
| confidence 低於 threshold | `HUMAN_REVIEW_REQUIRED`，不得建立 ERP command |
| 商品候選不唯一 | `HUMAN_REVIEW_REQUIRED`，reason `catalog_item_ambiguous` |
| 數量缺失／零／負數 | `HUMAN_REVIEW_REQUIRED`，reason `invalid_quantity` |
| 會員身份為 relay／無法驗證 | `HUMAN_REVIEW_REQUIRED` 或 `CUSTOMER_CONFIRMATION_REQUIRED` |
| 校點或 sales location 不明 | `HUMAN_REVIEW_REQUIRED`，不得跨 scope 猜測 |
| 人工補件後未完成會員確認 | 留在 `CUSTOMER_CONFIRMATION_REQUIRED` |
| 人工與會員確認完成 | 產生 immutable `XJ_CONFIRMED` snapshot |
| ERP mode `blocked` | `ERP_BLOCKED`，network calls = 0 |
| ERP mock 缺 SKU | `ERP_BLOCKED` 或 `manual_review`，不得自動補 mapping |
| ERP timeout | 受控 retry 或 `ERP_BLOCKED`，沿用 idempotency key |
| ERP unknown response | fail-closed，人工處理，不自動重送 |
| 相同 key、相同 payload | `REPLAYED`，不重複外部動作 |
| 相同 key、不同 payload | `CONFLICT_MANUAL_REVIEW`，不修改原 evidence |
| PII redaction／加密設定缺失 | 在入帳前停止，事件不得寫入明文 |
| company／store／location scope mismatch | 403／blocked，且不得建立 Adapter command |

## 10. 驗收條件

- 解析失敗、低信心、未知商品、缺欄位、scope 不明與 PII 失敗均可明確進入人工佇列。
- 人工 reviewer、manager、finance、維運與一般會員的資料範圍互不越權。
- 所有狀態變更都有 UTC、actor、原因、before／after fingerprint 與 audit reference。
- 任一 `needs_human_review`、`unknown_scope`、`unknown_sku`、`legal_entity_unconfirmed` 或 Adapter readiness failure 都不產生 ERP command。
- blocked／mock／isolated UAT 模式可證明 network calls、formal writes、payment writes、invoice writes 與 inventory writes 均為 0。
- 相同 idempotency key 的相同 payload 可 replay；不同 payload 會產生 conflict 且不修改既有 audit。
- 所有金額使用整數最小貨幣單位，所有時間為 UTC，PII 只在核准的加密欄位保存。
- 校鮮集 synthetic UAT 與其他專案資料完全隔離；不能引用萬佳鄉、雲鼎、捷州或 StallPay 的正式資料。
- 正式 external adapter、正式 payment、正式 invoice、正式 accounting、正式 device control 均在 owner gate 前維持 disabled。

## 11. 待 owner 決策

1. 校鮮集正式 product scope 與第一個試點客戶類型。
2. `company`、`cooperative`、`school`、`store`、`sales_location`、`pickup_location` 的正式 hierarchy。
3. 第一階段 order source：LINE、Web、POS、CSV、人工輸入的啟用順序。
4. `OrderParseResult` 正式 contract version、required fields 與 payload envelope。
5. confidence threshold、數量上限、商品匹配策略與人工覆核 SLA。
6. 人工 reviewer／manager 的正式角色名稱、資料範圍與高風險雙人核准規則。
7. ERP authoritative repository、owner、contract version、sandbox 與 mapping owner。
8. 「A 雲鼎」的正式名稱、repository、provider ID、scope 與是否為校鮮集第一個 ERP 目標。
9. 捷州 ERP 的正式 endpoint、認證、契約、mapping 與可用 sandbox；目前 repository 只證明 blocked／synthetic contract。
10. 第一階段是否只做 ERP pending／UAT，不啟用正式庫存、付款、發票、會計與稅務。
11. LINE Login／LIFF／官方帳號的 channel owner、訊息模板與通知責任。
12. OrderAI plugin 的正式登入、付款、發票、訂閱與 AI usage quota 邊界；目前 repository 已有自助註冊／方案查詢雛形，但未證明自助付款與自助發票已完成。
13. 校鮮集正式部署 owner、Railway project、domain、backup、monitoring 與 incident response。
14. direct／dealer／enterprise 三通路的方案、服務內容、價格版本與經銷分潤規則。

## 12. AI 成本評估前置工作

在進入正式模型選型前，先建立去識別化標註資料與固定評測流程：

- 記錄每一類來源訊息的字數／token 量、圖片／語音是否納入、預期每日與每月量；目前均為 `[TODO: 待人工確認]`。
- 以 `ILLMProvider` 抽象比較至少一個低成本模型與一個高準確度模型；模型名稱、單價與供應商需由 owner 確認。
- 量測商品／數量 exact match、人工覆核率、平均延遲、失敗率、重試率與每筆解析成本。
- 只有在成本與品質都達到 owner 閾值後，才允許調整校鮮集 confidence threshold；不可用展示頁數據宣稱準確率。
- AI usage quota 應依校鮮集方案與通路資料模型管理，`plans.channel` 維持 `direct`、`dealer`、`enterprise`；具體額度與價格版本為 `[TODO: 待人工確認]`。

## 文件邊界

本文件不代表校鮮集正式公司名稱、正式客戶、正式資料、正式 ERP、正式付款、正式發票、正式會計、正式稅務、正式設備控制、正式 SLA 或正式商業成果。所有未核准欄位均以 `[TODO: 待人工確認]` 標示。

© 2026 JCINN 捷州資訊. Concept showcase.  
§1 平台中立 · §2 原始碼主權 · §3 標準化部署 · §4 技術棧白名單 · §5 資料主權 · §6 AI 可替換 · §7 主權檢核
