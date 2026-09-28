# 校鮮集跨專案能力核驗與開發時程評估

**文件性質：**校鮮集專案專屬盤點與估時，不是正式開發規格、採購承諾或外部整合核准書  
**文件版本：**v0.1  
**日期：**2026-09-28  
**範圍：**OrderAI、雲鼎 ERP、捷州 ERP Adapter 與校鮮集第一階段人工覆核／OrderAI 狀態流程

## 1. 評估前提

校鮮集與萬佳鄉、雲鼎 ERP、StallPay 核心專案分開管理。本次只檢查公開 repository 的原始碼、分支、測試與 synthetic contract，不帶入其他專案的客戶資料、品牌文案、商品、門店、價格、ERP mapping、稅務規則、正式 endpoint 或 credential。

目前校鮮集仍是企業展示與 synthetic UAT 候選專案。以下估時必須在 owner 完成產品、資料、ERP、LINE、付款／發票及部署決策後才能轉為正式排程。

## 2. 已核驗的 repository 與 commit

| 項目 | Repository／分支 | 核驗 commit | 核驗結果 |
|---|---|---|---|
| OrderAI main | `pingoapple88/orderai-backend` / `main` | `1ec667cb76e725d63f2a896077793bbd664b3ecd` | Python FastAPI、SQLAlchemy、PostgreSQL、LINE／LLM Adapter、人工覆核與自助模組存在 |
| OrderAI 捷州 Adapter | `pingoapple88/orderai-backend` / `feat/jiezhou-erp-adapter` | `e118047100f2dfe1743c9a271b373aa220c43615` | 正式 provider 明確 blocked；另有 synthetic fake 與契約測試；無正式 endpoint／認證／正式契約 |
| MerchCore ERP main | `pingoapple88/merchcore-platform` / `main` | `1fa6cec80227f1f76bf7e5d89abbfd77e607e51f` | provider-neutral OrderAI ingress、ERP profile、scope、audit、replay、對帳 metadata boundary 存在 |
| 校鮮集原型 | `pingoapple88/Stallpay-lp` / `feat/xiaoxianji-enterprise-prototype` | `825b90fa8cca0abedfff495d18063d49b9cdd634` | `DEMO_MOCK` 展示原型；不代表正式產品、正式資料庫或正式外部服務 |

### 2.1 名稱與 endpoint 的待確認項目

- 雲鼎 ERP 在目前 ERP main 中以 `cloud_erp`／`cloud_yunding` provider-neutral identity 與 synthetic profile 出現；「A 雲鼎」是否為校鮮集正式目標、正式公司名稱、repository 與 owner，仍為 `[TODO: 待人工確認]`。
- OrderAI README 使用 `orderai.merchcore.ai` 作為專案描述；校鮮集是否使用此模組、是否另設 domain、Railway project 與正式網域，均為 `[TODO: 待人工確認]`。
- 任何正式 ERP、LINE、付款、發票或設備 endpoint 均未因本次核驗而取得使用權限。

## 3. 可運用能力總表

分類定義：

- `REUSE_AS_IS`：目前不建議標記任何項目。
- `EXTEND_VIA_ADAPTER`：可重用 provider-neutral 介面、驗證方法或測試方法，但必須建立校鮮集 mapping、fixture、scope 與 contract。
- `XJ_ONLY`：校鮮集原型或校鮮集專屬資料流，只能留在校鮮集，不回灌其他專案。
- `NEEDS_OWNER_DECISION`：缺少校鮮集 owner、正式契約、資料權責或外部連線核准。

| 能力 | 分類 | 可運用部分 | 目前不可運用部分 |
|---|---|---|---|
| OrderAI `ILLMProvider`／HTTP LLM Adapter | `EXTEND_VIA_ADAPTER` | provider-neutral LLM 介面、模型設定外部化、缺設定時停止解析 | 校鮮集模型、模型選擇、token 成本、正式 threshold 與產品型錄 mapping |
| OrderAI 風險判定 | `EXTEND_VIA_ADAPTER` | confidence、原文 evidence、數量上限、型錄命中、reason code、AI decision audit | 來源 threshold、正式商品、正式價格與 XJ 的狀態命名 |
| OrderAI LINE webhook ledger | `EXTEND_VIA_ADAPTER` | 驗簽、事件去重、source user HMAC、UTC、queued／processing／processed／failed | 校鮮集 LINE channel、官方帳號 owner、正式訊息模板與 retention |
| OrderAI P1 加密 draft | `EXTEND_VIA_ADAPTER` | Fernet 加密草稿、PII redaction、身份 unresolved、人工覆核前不建正式 order | 校鮮集 buyer identity、會員 schema、正式保存期限與加密金鑰管理 |
| OrderAI P1 review／customer confirmation／ERP outbox | `EXTEND_VIA_ADAPTER` | manager gate、人工核准、customer confirmation gate、blocked outbox、隔離送件 | 校鮮集正式狀態、角色、ERP authoritative source、正式資料庫 |
| OrderAI self-service registration／module status | `EXTEND_VIA_ADAPTER` | company／store 建立、idempotency、module status、方案通路欄位、audit | 校鮮集 onboarding、正式方案、訂閱、付款、發票與服務條款 |
| OrderAI LINE Login | `EXTEND_VIA_ADAPTER` | OAuth state、JWT／principal、`IAuthProvider` 方向 | 校鮮集身份綁定、合作社／校點範圍、正式 domain 與 channel 設定 |
| OrderAI 自助付款／自助發票 | `NEEDS_OWNER_DECISION` | 可列入產品化 roadmap 與 Adapter port | 本次 main 核驗未發現可直接視為完成的 payment／invoice runtime；provider、稅務與責任未定 |
| OrderAI 捷州 blocked provider | `EXTEND_VIA_ADAPTER` | blocked／fake／pending intent、timeout／unknown／manual_review／idempotency 測試方法 | 正式捷州 endpoint、auth、欄位、錯誤契約與正式送件 |
| 雲鼎 ERP `OrderRecognitionPayload`／`OrderDraft` | `EXTEND_VIA_ADAPTER` | typed payload、strict fields、整數最小貨幣單位、UTC、總額重算 | 直接套用 synthetic tenant、company、sales location、UUID、SKU |
| 雲鼎 ERP `ERPAdapterRequestEnvelope` | `EXTEND_VIA_ADAPTER` | command、audit、scope 綁定；scope mismatch fail-closed | 校鮮集正式 legal entity、公司、校點與 ERP mapping |
| 雲鼎 ERP compatibility evaluator | `EXTEND_VIA_ADAPTER` | company／location／legal entity／SKU／currency／minor units／idempotency／audit 檢核 | XJ 權威型錄、正式 ERP capability profile |
| 雲鼎 ERP `cloud_erp` profile | `NEEDS_OWNER_DECISION` | 作為 profile contract 形狀與 synthetic UAT 參考 | 不是 A 雲鼎正式 profile；目前 `production_endpoint=None`、write false |
| 雲鼎 ERP reconciliation boundary | `EXTEND_VIA_ADAPTER` | metadata-only observation、UTC period、整數金額、fingerprint chain、replay／conflict／manual review | 正式付款 settlement、會計入帳、稅務申報與銀行／支付資料 |
| LINE notification contract | `EXTEND_VIA_ADAPTER` | `INotificationProvider`、idempotency、tenant scope、delivery result | 校鮮集通知模板、接收人、排程、官方帳號與訊息責任 |
| 校鮮集展示原型與三溫層畫面 | `XJ_ONLY` | 作為展示 journey、synthetic fixture 與業務說明 | 不可視為設備 API、庫存扣減、門鎖控制或正式營運證據 |
| 正式 ERP endpoint／migration／credential／商品 mapping | `NEEDS_OWNER_DECISION` | 僅可建立 decision gate 與 mapping template | 本次禁止直接複製或連線 |

## 4. OrderAI main 實作核驗

### 4.1 目前可參考的核心

1. `app/services/order_risk_service.py`
   - 從資料庫設定讀取 confidence threshold、每單品項上限與單列數量上限。
   - 檢查整體 confidence、品項 confidence、原文 evidence、數量格式、同店型錄命中。
   - 任一檢查失敗即回傳 `needs_review`，不允許自動通過。
   - audit 只記錄 reason code、threshold、provider、confidence、item count 與 source SHA-256，不把原始 LINE 文字、電話與 email 放進 audit JSON。

2. `app/services/p1_intake_service.py`
   - LINE 事件先寫最小事件帳本，使用 event ID 去重與 source user HMAC。
   - PII／草稿以 Fernet 加密保存。
   - 圖片／音訊／檔案未配置 OCR／STT 時進入人工確認，不自動解析。
   - 商品只允許同店型錄命中，並且要有外部化 ERP product ID mapping 才可形成 ERP pending request。
   - 解析完整也不代表可送 ERP；仍須客戶確認與人工覆核。

3. `app/services/p1_delivery_service.py`
   - 對話 state 為 `needs_human_review`、`awaiting_customer_confirmation`、`awaiting_erp_delivery`、`closed`。
   - 僅 owner／manager 可操作 review 與 dispatch。
   - 未確認前不能排入 ERP outbox；ERP 送件前還要通過隔離 target／UAT marker／HTTPS／allow-list gate。
   - Adapter 失敗寫入 controlled error code，outbox status 轉 `failed`，不把失敗當成功。

4. `app/services/module_service.py` 與 `app/api/v1/module.py`
   - 已有自助註冊、模組 health／manifest、方案依 `direct`／`dealer`／`enterprise` 查詢、module status 與 idempotency registration。
   - `plans` 的 `channel` 與同名不同通路唯一性，可作校鮮集商業資料模型參考。
   - 目前仍需校鮮集自己的 onboarding、方案 owner、subscription、payment、invoice、服務條款與 deployment contract。

5. `app/api/v1/auth.py`
   - repository 中已有 LINE Login／OAuth state／JWT principal 的方向。
   - 校鮮集若採用，必須重新定義 company／cooperative／school／store scope，不可把 OrderAI 現有 store mapping 當成校鮮集正式層級。

### 4.2 OrderAI main 測試結果

本次先安裝 pytest 與必要依賴後重跑：

```text
python3 -m pytest -q \
  tests/test_order_risk_service.py \
  tests/test_worker_fail_closed_scenarios.py \
  tests/test_p1_intake.py \
  tests/test_orders_reject.py \
  tests/test_line_worker.py
```

結果：**未完成**。共 38 個案例因 sandbox 沒有啟動 PostgreSQL，連線 `localhost:5432` 被拒絕；不是 assertion failure，也不能據此宣稱 OrderAI main 全部通過。

需要在隔離 PostgreSQL／Docker Compose／CI database 上重跑後，才能把下列能力列為校鮮集可引用的 runtime evidence：

- 風險判定資料庫測試。
- LINE 事件去重與 worker 行為。
- P1 加密 draft、人工覆核與 blocked outbox。
- 跨 company／store 的 reject scope。

## 5. OrderAI 捷州 Adapter branch 核驗

來源：`feat/jiezhou-erp-adapter`，commit `e118047100f2dfe1743c9a271b373aa220c43615`。

### 5.1 實作狀態

- `JiezhouBlockedErpIngestProvider` 明確拒絕送件，理由包含 endpoint、認證、欄位與錯誤契約尚未確認。
- `FakeJiezhouErpIngestProvider` 只接受 provider-neutral `PendingOrderIntent`，回傳 `pending` 或 `manual_review`。
- fake provider 只在 memory 運作，不建立付款、庫存、出貨、發票或正式訂單副作用。
- synthetic fixture 的 `contract_status` 是 `[TODO: 待人工確認]`。
- 所有正式 delivery 仍為 blocked，不能把 fake `pending` 當成捷州 ERP 已入庫。

### 5.2 測試結果

```text
python3 -m pytest -q \
  tests/test_jiezhou_erp.py \
  tests/test_jiezhou_contract_smoke.py \
  tests/test_erp_ingest_compatibility.py \
  tests/test_erp_readiness.py \
  tests/test_erp_conformance.py \
  tests/test_erp_traceability.py

37 passed in 0.46s
```

這 37 個通過案例只證明 synthetic contract、blocked provider、fake outcome、scope／mapping／timeout／unknown／idempotency 與 evidence 方法；不證明正式捷州 ERP 可連線。

## 6. 雲鼎 ERP main 核驗

來源：`pingoapple88/merchcore-platform`／`main`，commit `1fa6cec80227f1f76bf7e5d89abbfd77e607e51f`。

### 6.1 可運用的 provider-neutral 能力

- `OrderRecognitionPayload`：嚴格檢查來源、tenant／company／sales location、外部訂單號、currency、line、confidence、human review flag 與 idempotency。
- `OrderDraft`：重算 line total 與總額；拒絕 fractional／float money；時間需 timezone-aware 並正規化 UTC。
- `OrderIngestResult`：`accepted`、`needs_human_review`、`rejected` 與 `ready_for_adapter` 綁定，review／rejected 不可產生 ERP command。
- `OrderIngestAuditEvent`：每次 decision 都保存 draft、tenant、company、sales location、idempotency、reason code 與 UTC。
- `ERPAdapterRequestEnvelope`：command、audit event 與 scope 必須逐欄一致，才可進 Adapter。
- compatibility evaluator：檢查 adapter capability、company、sales location、legal entity、SKU、currency、minor units、idempotency、UTC 與 audit。
- audit store：同 company＋idempotency key 的同 payload replay；不同 payload 產生 conflict，不接受覆寫。
- profile gate：profile unknown、scope mismatch、capability missing 與 idempotency replay 均 fail-closed。

### 6.2 雲鼎／捷州 profile 的重要限制

目前 ERP main 的 `CLOUD_ERP_PROFILE` 與 `JIEZHOU_ERP_PROFILE` 都是 synthetic profile：

- `production_endpoint=None`。
- `production_write_allowed=False`。
- synthetic scope、SKU、currency 與 legal entity 只供 contract fixture。
- profile compatibility 通過只代表 provider-neutral command 與 synthetic allow-list 相容。
- profile 測試不代表雲鼎或捷州正式資料可寫入。

### 6.3 雲鼎 ERP 測試結果

```text
PYTHONPATH=. python3 -m pytest -q \
  tests/test_order_ingest_contract.py \
  tests/test_order_ingress_orchestration.py \
  tests/test_order_recognition_ingress_service.py \
  tests/test_erp_profiles.py \
  tests/test_yunding_first_mapping.py \
  tests/test_reconciliation_settlement_boundary.py

93 passed in 0.50s
```

這 93 個通過案例證明 provider-neutral ingress、scope、legal entity、money、audit、replay、profile gate 與 metadata-only reconciliation contract 的 synthetic 行為；不證明校鮮集已完成 ERP mapping 或正式財務對帳。

## 7. 財務對帳與自助功能的可用邊界

### 7.1 對帳

ERP `reconciliation_settlement_boundary.py` 是 `TEST_ONLY`、`DENY_NO_NETWORK`、`FORMAL_NO_GO` 的 metadata-only boundary，具備：

- settlement period UTC 化與 closed period 阻擋。
- amount 使用 integer minor units。
- request／response／reconciliation fingerprint 與 digest chain。
- exact replay、idempotency conflict、manual review、rollback metadata。
- provider／scope／tenant mismatch fail-closed。

可帶入校鮮集的是 interface、metadata、fingerprint、replay 與測試方法；不可把它宣稱為正式付款 settlement、會計入帳、稅務申報或銀行對帳。

### 7.2 OrderAI 自助註冊、付款與發票

目前 OrderAI main 可見：

- module health／manifest。
- module self-service registration。
- `direct`／`dealer`／`enterprise` plan channel 查詢。
- module status 與 AI usage limit 欄位。
- LINE Login／OAuth state／JWT 的實作方向。

本次 main 核驗沒有找到可直接視為完成的校鮮集自助付款與自助發票流程。若要符合「登入、付款、發票」的產品化需求，至少需要另行確認：

- `IPaymentProvider`、`IInvoiceProvider`、`IAccountingProvider` 的校鮮集 contract。
- sandbox／正式 provider、退款／作廢／折讓／未知結果策略。
- Railway deployment owner、domain、webhook、secret rotation 與 audit owner。
- `plans.channel`、subscription、billing record、invoice record 與正式費率版本。
- AI usage quota 的計價與通路規則；模型成本必須先以實際訊息量和模型選擇評估，不能由展示數據推估。

## 8. 校鮮集第一階段建議採用順序

### Phase 0：Owner decision gate

先確認 product scope、第一個試點、資料 hierarchy、Order source、人工角色、ERP authority、LINE channel、付款／發票邊界、部署 owner 與三通路方案資料模型。

### Phase 1：XJ synthetic contract

建立校鮮集自己的：

- `xj.order_parse_result.v0.1`。
- canonical states 與 transition table。
- company／cooperative／school／store／sales location scope。
- product／SKU／mapping version。
- synthetic fixture manifest、data cleanup policy、evidence harness。

### Phase 2：人工覆核與 OrderAI plugin

先完成：

- LINE／Web source ledger。
- OrderAI parse draft、confidence、reason codes、PII redaction。
- reviewer／manager RBAC。
- customer confirmation。
- provider-neutral ERP pending intent。
- blocked／mock／isolated UAT Adapter。
- audit、idempotency、replay／conflict。

### Phase 3：單一 ERP isolated UAT

優先選 owner 已提供 contract、mapping、scope、sandbox 與 test data 的 ERP。若「A 雲鼎」仍未具備正式資料，先以 `cloud_erp` synthetic profile 做 XJ UAT，不宣稱正式雲鼎整合。

捷州 ERP 需獨立完成 contract、endpoint、auth、mapping、response classification 與責任核准；不能因為 synthetic profile 與雲鼎共用 shape，就把雲鼎 mapping 套給捷州。

### Phase 4：可銷售試點

核心先以人工取貨／人工庫存／報表匯出為必要路徑；智販機、取物櫃、iMin F1、三溫層與正式付款／發票列為可選整合，逐一通過 sandbox、失敗情境、audit、責任與 release gate。

## 9. 開發時程估算

### 9.1 估算假設

- 估算單位為 person-day（PD），不是固定報價，也不是承諾日期。
- 假設團隊：2 位後端、1 位前端、0.5 位 QA／驗證、0.25 位產品／整合 owner。
- Production 技術棧依專案規範：Python FastAPI、SQLAlchemy、PostgreSQL、Railway 等自有基礎設施；不使用 TypeScript／tRPC／Drizzle／MySQL。
- 外部 ERP、LINE、付款、發票與設備 owner 能在 gate 前提供書面契約與 sandbox；否則只做 blocked／mock／isolated UAT。
- 估算不包含長時間外部等待、稅務／法律審查、硬體採購、廠商現場施工或未確認的資料清理。

### 9.2 分項估時

| 工作包 | 內容 | 估算 PD | 估算日曆時間 | 前置條件 |
|---|---|---:|---:|---|
| XJ owner decision 與 contract freeze | 產品、角色、scope、source、OrderParseResult、狀態、資料 owner | 8–12 | 1–2 週 | owner 可定期決策 |
| XJ synthetic domain／DB／migration | company／cooperative／school／store、source ledger、draft、review、outbox、audit | 15–25 | 2–3 週 | contract freeze |
| OrderAI 人工覆核流程 | confidence、reason code、review queue、customer confirmation、RBAC、PII、replay | 20–30 | 3–4 週 | XJ contract、PostgreSQL UAT |
| OrderAI plugin／自助註冊 | MerchCore manifest、module registration、LINE Login binding、AI quota、i18n、通路資料 | 12–20 | 2–3 週，可與人工覆核並行 | auth owner、domain、plans owner |
| LINE 通知與排程 | `INotificationProvider`、模板、delivery log、retry／unknown policy、scheduled messages | 10–16 | 2–3 週 | LINE channel、接收人與模板核准 |
| 單一 ERP provider-neutral UAT | profile、scope、mapping、command、audit envelope、mock／blocked／replay harness | 15–25 | 2–3 週 | contract、mapping、synthetic data |
| 雲鼎正式／隔離 Adapter | 依 A 雲鼎書面契約建立 transport、auth、timeout、response mapping | 25–40 | 4–6 週 | A 雲鼎 endpoint、sandbox、owner、credential 流程 |
| 捷州正式／隔離 Adapter | 依捷州書面契約建立 transport、auth、pending contract、response mapping | 25–40 | 4–6 週 | 捷州正式契約；目前仍 blocked |
| 商品／庫存／人工取貨 | XJ SKU、inventory movement、reserve／release／deduct 語義、pickup ledger | 25–40 | 4–6 週 | inventory authority、ERP mapping |
| 對帳／報表／匯出 | settlement observation、reconciliation item、差異佇列、CSV／報表、audit | 18–30 | 3–5 週 | payment／ERP owner、對帳鍵 |
| 自助付款／發票／會計 draft | payment、refund、invoice、accounting export、unknown／manual review | 25–45 | 4–7 週 | provider sandbox、稅務與會計 owner |
| AI 成本與品質基線 | 去識別化標註資料、模型比較、token／延遲／人工率／exact match | 3–5 初始；持續評估 | 1–2 週初始 | synthetic／去識別化資料、模型供應商 |
| iMin／智販機／取物櫃／三溫層 | device adapter、狀態查詢、開門／取出分離、異常補救、現場 UAT | 35–60 | 6–10 週 | 硬體、API、SLA、現場 owner |

### 9.3 里程碑估算

| 里程碑 | 內容 | 預估總投入 | 日曆時間（可並行時） |
|---|---|---:|---:|
| M0：XJ 第一階段 contract freeze | owner decision、synthetic fixture、狀態與 scope 定稿 | 8–12 PD | 1–2 週 |
| M1：人工覆核 synthetic slice | source → parse → review → confirmation → blocked／mock UAT | 45–70 PD | 4–6 週 |
| M2：單一 ERP isolated UAT | provider-neutral command、mapping、audit、replay、evidence | 65–100 PD | 7–11 週（含 M1 後段並行） |
| M3：可收費試點核心 | Core Workspace、商品／團購、會員、訂單、人工庫存、人工取貨、LINE 基礎通知、對帳匯出 | 120–180 PD | 12–18 週 |
| M4：標準 SaaS／自助商業化 | onboarding、方案、訂閱、付款、發票、usage quota、支援與 release gate | 190–300 PD | 16–24 週 |
| M5：雙 ERP＋設備整合 | 雲鼎與捷州獨立 Adapter，加上 iMin／智販機／取物櫃／三溫層 | 300–450 PD | 24–36 週 |

**估算使用方式：**

- 若只有 1 位後端，日曆時間通常接近 PD 總量除以一位工程師可用容量，不能直接套用上表。
- 若 A 雲鼎或捷州在中途才提供 endpoint／契約，該 provider 工作包需重新估算，不把 blocked synthetic 工作誤算成正式整合完成。
- 付款／發票、設備、稅務與現場硬體的等待時間應另加 20%–30% schedule buffer；實際 buffer 由專案 owner 核准。

## 10. 第一階段最小可交付範圍

### 可列入第一階段

- XJ 專屬 synthetic source ledger。
- XJ 專屬 OrderAI parse draft contract。
- 低信心／商品不明／缺欄位／scope mismatch 的人工覆核佇列。
- reviewer／manager 最小權限與 audit。
- customer confirmation gate。
- blocked／mock／isolated UAT ERP Adapter。
- idempotency、replay、payload conflict、PII redaction 與 evidence harness。
- AI 成本／品質基線，不宣稱準確率或固定模型成本。
- `plans.channel` 的 `direct`、`dealer`、`enterprise` 資料模型預留，不公開未核准價格。

### 不列入第一階段正式啟用

- 正式雲鼎 ERP 或捷州 ERP 寫入。
- 正式庫存扣減、付款、發票、會計入帳與稅務申報。
- iMin F1 正式收銀／列印、智販機／取物櫃開門與三溫層感測控制。
- 真實校鮮集會員、學校、合作社、商品、價格或訂單資料。
- 直接把校鮮集 Cloudflare Preview 當成客戶資料環境。

## 11. 開發前阻塞條件

1. XJ 正式 product scope 與第一個試點客戶未確認。
2. XJ company／cooperative／school／store／sales location hierarchy 未確認。
3. XJ `OrderParseResult` contract、threshold、reason code 與狀態機未核准。
4. A 雲鼎正式身份、repository、owner、契約、sandbox、mapping 與資料責任未確認。
5. 捷州正式 endpoint、auth、契約與 sandbox 未提供；目前只能 blocked／synthetic。
6. OrderAI main 關鍵 DB 測試在本 sandbox 因 PostgreSQL 未啟動而無法完成，需 isolated PostgreSQL／CI 重跑。
7. LINE channel owner、Login／LIFF／官方帳號、通知模板與資料保存責任未確認。
8. 付款、發票、會計、稅務與自助商業化責任未確認。
9. Railway project、domain、backup、monitoring、secret rotation、incident response owner 未確認。
10. AI 使用量、模型、token、人工覆核率與成本上限未確認，不能先承諾 AI 單筆成本或方案額度。

## 12. 測試證據摘要

| 測試組合 | 結果 | 解讀 |
|---|---|---|
| OrderAI main：risk／worker／P1／reject／LINE worker | **未完成**；38 案例因 `localhost:5432` PostgreSQL connection refused | 需在隔離 PostgreSQL／CI 重跑；不能宣稱 main runtime 全通過 |
| OrderAI 捷州 branch：Jiezhou／contract／compatibility／readiness／conformance／traceability | **37 passed in 0.46s** | synthetic／blocked contract evidence；不代表正式捷州 ERP 可用 |
| 雲鼎 ERP main：ingest／orchestration／recognition／profiles／mapping／reconciliation | **93 passed in 0.50s** | provider-neutral synthetic evidence；不代表校鮮集正式 mapping 或正式 ERP write |

## 13. 建議的下一個工程輸入

正式交給開發前，應先由 owner 回填以下三份校鮮集專屬輸入：

1. `XJ_PHASE1_DECISION_RECORD.md`：scope、角色、資料 owner、ERP authority、LINE、付款／發票與 deployment owner。
2. `xj-order-parse-result-v0.1.json`：固定 schema、欄位、reason code、threshold 與 fixture。
3. `xj-erp-mapping-manifest-v0.1.json`：company／store／location／SKU／legal entity／currency／mapping version 與 provider mode。

在三份輸入未核准前，release gate 維持：

```text
formal_connections = false
formal_inventory_write = false
formal_payment = false
formal_invoice = false
formal_tax_filing = false
formal_device_control = false
release_gate = BLOCKED
```

## 文件邊界

本文件不代表校鮮集正式公司名稱、正式客戶、正式資料、正式 ERP、正式付款、正式發票、正式會計、正式稅務、正式設備控制、正式 SLA 或正式商業成果。所有未核准欄位均以 `[TODO: 待人工確認]` 標示。

© 2026 JCINN 捷州資訊. Concept showcase.  
§1 平台中立 · §2 原始碼主權 · §3 標準化部署 · §4 技術棧白名單 · §5 資料主權 · §6 AI 可替換 · §7 主權檢核
