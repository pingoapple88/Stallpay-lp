# 校鮮集第一階段需求與現有資產盤點

**文件版本：**v0.1

**盤點日期：**2026-09-18

**專案：**校鮮集企業專案 Chat

**工作範圍：**需求與現有資產盤點，不代表正式產品規格，也不直接寫入正式產品程式碼。

## 一、盤點結論

校鮮集目前可確認的資產，是一個獨立的企業展示原型與一組已標示邊界的展示文件。原型位於 `pingoapple88/Stallpay-lp` 的 `feat/xiaoxianji-enterprise-prototype` 分支，最新已知 HEAD 為 `bd26c759e5a56dc953bb21eb0c0136aefbb22eef`。這個分支只能代表校鮮集已有的展示線索，不代表正式產品規格、正式客戶資料、正式 ERP、正式設備或正式服務承諾。

本次三方能力盤點沒有發現任何一項可以在目前證據下直接標記為 `REUSE_AS_IS`。原因不是抽象設計不可參考，而是校鮮集的產品定位、資料 owner、ERP authoritative repository、正式 mapping、正式 endpoint、責任邊界與契約版本尚未由 owner 確認。

目前最合理的分類如下：

| 能力 | 目前判定 | 可參考範圍 | 不可直接帶入的範圍 |
|---|---|---|---|
| OrderAI P1 `OrderParseResult` 與狀態流程 | `NEEDS_OWNER_DECISION` | Screen View Model、adapter boundary、synthetic fixture、focused-test 方法與 fail-closed 思路 | OrderParseResult schema、正式狀態機、產品／品項 mapping、confidence 閾值、endpoint、實作與來源資料 |
| `IErpIngestProvider`、blocked／mock／HTTP Adapter、商品 mapping | `NEEDS_OWNER_DECISION` | ERP authoritative boundary、normalized adapter 結果、synthetic fixture、timeout／retry／idempotency／dead-letter／reconciliation 測試方向 | 正式 ERP、正式 schema、migration、endpoint、credential、商品／門店／價格 mapping 與庫存規則 |
| T9 `IInvoiceProvider`、`IReconciliationAdapter`、`IAccountingProvider` 與會計／稅務 draft | `EXTEND_VIA_ADAPTER` | provider-neutral port、draft completeness、minor units、UTC、opaque reference、fail-closed、audit 與 synthetic harness 方法 | provider-specific runtime、正式發票／會計／稅務資料、正式申報、帳號、endpoint、稅率與會計科目 |

上述判定只適用於本次允許閱讀的文件與盤點輸出。它不表示其他 repository 的實際程式碼、正式資料或正式測試已被校鮮集核准。

## 二、校鮮集專案邊界表

### 2.1 目前已知與待確認項目

| 邊界項目 | 目前校鮮集可確認內容 | 狀態 | 第一階段 owner 必須確認的事項 |
|---|---|---|---|
| Product scope | 目前只有「多校／合作社／食品團購企業展示原型」的展示線索。正式產品定位尚未核准。 | `NEEDS_OWNER_DECISION` | 是否正式定位為多校團購營運平台、合作社平台、企業福利平台，或其他產品；第一階段哪些模組可承諾交付。 |
| User roles | 原型展示企業管理者、合作社窗口、教職員工、學生、財務人員、設備維運人員與一般會員等概念角色。 | `NEEDS_OWNER_DECISION` | 正式角色名稱、角色階層、合作社／校點資料範圍、人工覆核權限與高風險操作雙重核准規則。 |
| Company／legal entity／store | `company_id`、合作社、校點與 store scope 只能作為治理概念參考；校鮮集法人與門店結構未確認。 | `NEEDS_OWNER_DECISION` | 法人、品牌、企業、合作社、校點、配送點、取貨點與設備的上下層關係；各資料 owner 與責任主體。 |
| Order source | 原型展示 LINE／LIFF、Web、POS、團購、CSV 與人工流程的概念，但沒有正式 source contract。 | `NEEDS_OWNER_DECISION` | 第一階段實際啟用哪些來源；來源優先順序；每個來源的 idempotency、訂單 owner 與人工補件流程。 |
| OrderAI input | 原型展示文字訊息、低信心與人工介入；尚未確認文字、圖片、語音或人工輸入是否納入正式範圍。 | `NEEDS_OWNER_DECISION` | OrderAI 輸入種類、解析欄位、confidence 閾值、PII redaction、人工覆核角色、重試與 dead-letter 規則。 |
| Human confirmation | 原型展示低信心時停止自動建單並交人工。正式核准角色與責任未確認。 | `NEEDS_OWNER_DECISION` | 誰可確認、誰可退回、誰可改數量／價格／校點、誰可完成建單，以及每項操作的 audit 欄位。 |
| Product／SKU | 原型只有合成商品、SKU 與展示數字，沒有校鮮集正式型錄。 | `NEEDS_OWNER_DECISION` | 校鮮集 product／SKU owner、唯一識別、規格、包裝、批次、效期、溫層、價格版本與 ERP product ID mapping owner。 |
| Inventory authority | 原型展示可售、預留、實體取出與多校庫存概念，未形成正式 authoritative source。 | `NEEDS_OWNER_DECISION` | ERP、校鮮集或其他系統誰是庫存真相；reserve／release／deduct／dispense／reconcile 的語義與時點。 |
| ERP authority | 目前沒有校鮮集 ERP owner、repository、branch、commit 或正式 endpoint 的確認。 | `NEEDS_OWNER_DECISION` | authoritative ERP repository、owner、contract version、sandbox、同步責任、mapping version、資料庫與 rollback owner。 |
| Payment boundary | 原型不執行正式付款；付款服務商與付款結果 owner 未確認。 | `NEEDS_OWNER_DECISION` | 第一階段是否付款、付款服務商、付款狀態來源、退款責任、未知結果處理與對帳 owner。 |
| Invoice boundary | 原型只展示 iMin F1 收銀／發票畫面，不代表正式發票開立。 | `NEEDS_OWNER_DECISION` | 發票 provider、發票 owner、正式資格、sandbox、作廢／折讓／更正流程與責任歸屬。 |
| Tax boundary | 原型不宣稱稅率、課稅別、申報期限或申報結果。 | `NEEDS_OWNER_DECISION` | 會計與稅務 owner、稅務分類、稅率、申報責任、會計科目與正式核准流程。 |
| Data owner | 展示資料均為 synthetic；正式會員、訂單、商品、庫存與對帳資料 owner 未確認。 | `NEEDS_OWNER_DECISION` | 資料擁有者、處理者、保存期限、刪除／匯出權、PII 加密／遮罩、備份與還原責任。 |
| Deployment owner | 原型可由 GitHub branch 與 Cloudflare Pages Preview 展示；正式部署 owner 未確認。 | `NEEDS_OWNER_DECISION` | 捷州資訊自有基礎設施、正式環境、網域、監控、備份、release gate、維運與事件通報 owner。 |
| Commercial channel | 尚未有校鮮集正式方案或價格。 | `NEEDS_OWNER_DECISION` | `direct`、`dealer`、`enterprise` 三通路方案、導入責任、價格版本、服務內容與經銷分潤規則。 |

### 2.2 明確禁止跨專案套用

以下項目不得從萬佳鄉、雲鼎 ERP、StallPay 核心專案或其他 repository 直接帶入校鮮集：

- 客戶資料、品牌文案、商品、SKU、門店、校點、價格或會員資料。
- ERP endpoint、service ID、HMAC secret、商品 ID、正式 API credential 或正式資料庫。
- migration、正式 schema、正式 mapping、正式帳務資料與正式資料保留規則。
- 支付、發票、稅務、會計、設備或申報 endpoint。
- 分潤、方案、費率、稅率、佣金、退款或福利規則。

如果日後採用共用能力，必須在校鮮集專屬變更紀錄中記錄來源 repository、branch、commit、contract 版本、測試證據與校鮮集客製 mapping；未完成 owner 核准前，維持 `NEEDS_OWNER_DECISION` 或 `CENTRAL_GATE／BLOCKED`。

## 三、現有校鮮集資產盤點

### 3.1 校鮮集專屬原型資產

| 資產 | 來源 | 可確認內容 | 限制 |
|---|---|---|---|
| 單頁展示原型 | `pingoapple88/Stallpay-lp`／`feat/xiaoxianji-enterprise-prototype`／HEAD `bd26c759e5a56dc953bb21eb0c0136aefbb22eef` | 多校、合作社、LINE、ERP、福利、iMin、智販機、取物櫃與三溫層異常畫面 | `DEMO_MOCK`；沒有正式 API、資料庫、會員、訂單或付款寫入 |
| `XIAOXIANJI_PREVIEW.md` | 同一校鮮集 branch | 明確記錄原型範圍、Cloudflare Preview、LINE／ERP／設備邊界 | 是展示說明，不是正式產品規格 |
| `XIAOXIANJI_THERMAL_EXCEPTION_REMEDIATION.md` | 同一校鮮集 branch | 三溫層、開門失敗、物品未取出、結果不明、人工處理與 fail-closed 概念 | 設備型號、感測器、API、SLA 與責任均為 TODO |
| `IMIN_F1_AND_SETTLEMENT_OPERATIONS.md` | 同一校鮮集 branch | iMin F1 收銀／列印與福利結算的展示操作說明 | 不代表正式支付、發票、稅務、ERP 或設備整合 |
| `XIAOXIANJI_PRODUCTIZATION_ROADMAP.md` | 同一校鮮集 branch，commit `bd26c759e5a56dc953bb21eb0c0136aefbb22eef` | 商業化階段、模組邊界、雙通路方案與正式驗收門檻 | 是產品化藍圖，不是正式開發規格 |
| QA 與 Cloudflare 證據 | `QA_BROWSER_NOTES.md` 與既有 Pages check | 已驗證展示頁與互動原型可載入 | 只能證明展示流程，不證明正式服務或設備控制 |

### 3.2 原型中可以保留的治理方向

下列方向屬於校鮮集自身目前已記錄的治理原則，可作為後續需求確認時的候選基線：

- `DEMO_MOCK`、synthetic fixture 與 formal connection false 的明確區分。
- OrderAI 低信心、商品不明或校點衝突時停止自動建單。
- 開門結果不明、物品取出不明或溫層不明時採 fail-closed。
- 庫存預留、庫存扣減與實體取出確認分開建模。
- 付款、發票、設備、LINE 與 LLM 以 Adapter 隔離。
- 所有正式狀態變更保留 audit、UTC、idempotency 與 PII 邊界。

這些方向仍需轉化成校鮮集正式 owner 核准的 contract 與驗收條件，不能因為原型畫面存在就視為正式實作已完成。

## 四、共用能力對照表

### 4.1 OrderAI P1：`OrderParseResult` 與狀態流程

**來源識別**

- Repository：`pingoapple88/orderai-backend`
- Branch：`feat/orderai-parse-self-service-hardening`
- Commit：`99279894d347f2dd2d19a07735d7e937e0547f39`
- Contract：文件提及 `Contract v1.8`，但沒有提供 `OrderParseResult` 專屬契約版本，因此專屬版本為 `[TODO: 待人工確認]`。
- 證據文件：`WO-T5-ORDERAI-SELF-SERVICE-UI-WEEK1.md`、`MerchCore跨模組事件契約差異矩陣v1.8(W2補正版).md`、共享 `README.md`。

**分類：`NEEDS_OWNER_DECISION`**

可參考的 provider-neutral 能力包括 Screen View Model、UI 與 service 的 adapter boundary、synthetic fixture、focused test 方法、PII redaction 與低信心時 fail-closed 的思路。文件宣稱有 `orderai.parse_result` 畫面、`/orderai/parse-result` 路由、`needs_review`、`manual_review`、queue、重試與 dead-letter 概念，但指定輸入沒有提供 OrderParseResult 實際 schema、runtime 輸出、fixture manifest 或測試 stdout，因此不能把這些內容標記為校鮮集已驗證能力。

**校鮮集 mapping：**

- `OrderParseResult` 是否是 UI view model、跨模組事件或兩者皆有：[TODO: 待人工確認]。
- 欄位名稱、型別、必填性、版本與 envelope：[TODO: 待人工確認]。
- 商品／品項識別、數量、價格 minor units、currency、confidence、PII redaction 與 `audit_reference`：[TODO: 待人工確認]。
- `needs_human_review`、`awaiting_customer_confirmation`、`awaiting_erp_delivery`、`closed` 是否為正式 canonical states，以及 transition table：[TODO: 待人工確認]。
- `company_id`、`store_id`、`sales_location_id` 或其他校鮮集 scope 欄位：[TODO: 待人工確認]。

**測試證據限制：**

來源工作單只列出 pytest、compileall、PII／外部連線 grep、L0／L1、自審與交接證據應如何執行，沒有提供本次可核對的 stdout、exit code、fixture 或 report。因此不可宣稱 OrderParseResult、狀態流程、RWD、PII scan 或正式隔離測試已通過。

**禁止直接重用：**來源專案的 UI、adapter、fixture、測試實作與任何正式資料，不得複製到校鮮集。即使後續 owner 核准，也應先以校鮮集專屬 contract、fixture 與 adapter mapping 重新驗證。

### 4.2 ERP ingest、blocked／mock／HTTP Adapter 與商品 mapping

**來源識別**

- 文件明示 repository 線索：`pingoapple88/stallpay-v2`。
- Branch：指定文件沒有確認 IErpIngestProvider 能力的正式 branch，為 `[TODO: 待人工確認]`。
- Commit：未提供，為 `[TODO: 待人工確認]`。
- Contract：未宣告 IErpIngestProvider 專屬版本；相鄰事件契約為 `JCINN-CONTRACT-2026-V1.8`，T9 normalized contract 為 `v0.1`，兩者都不能直接視為 IErpIngestProvider contract。
- 證據文件：`WO-T8-ERP-INVENTORY-INTEGRATION-WEEK1.md`、`MerchCore跨模組事件契約差異矩陣v1.8(W2補正版).md`、共享 `README.md`。

**分類：`NEEDS_OWNER_DECISION`**

文件層級可以參考的 provider-neutral boundary 是：ERP 作為 authoritative source；T2 保有訂單／叫號事實；T7 保有設備庫存／出貨事實；T8 負責 ERP mapping、同步與對帳；不得建立第二套 ERP 庫存真相。另可參考 generic fake adapter 或 sandbox client 應涵蓋成功、缺 SKU、庫存不足、重送、timeout、partial sync、對帳差異與 dead-letter 等情境。

**校鮮集 mapping：**

- ERP owner、repository、branch、HEAD、data owner、migration owner、test database owner：[TODO: 待人工確認]。
- IErpIngestProvider 的 request／normalized result schema 與版本：[TODO: 待人工確認]。
- blocked／mock／HTTP 三種模式的狀態機：[TODO: 待人工確認]。
- HTTP authentication、signature、timeout、retry、idempotency、rate limit、partial sync 與 dead-letter：[TODO: 待人工確認]。
- `product_id`、SKU、ERP product code、`store_key`、貨道、庫存欄位、mapping version 與變更責任人：[TODO: 待人工確認]。
- reserve／release／deduct／dispense／reconcile 的業務語義與正式 owner：[TODO: 待人工確認]。

**測試證據限制：**

`WO-T8-ERP-INVENTORY-INTEGRATION-WEEK1.md` 只列出未來交付應具備的 fixture path、harness path、test command、expected exit code 與 evidence path，沒有提供實際執行輸出。因此目前只能說明測試範圍構想，不能宣稱 ERP ingest、HTTP adapter 或商品 mapping 已驗證。

**禁止直接重用：**不得使用來源專案的正式 ERP endpoint、credential、schema、migration、raw response、商品／門店／價格資料。`JCINN-CONTRACT-2026-V1.8` 的 envelope 欄位只能作相容性參考，不得直接當作校鮮集 ERP contract 或 mapping。

### 4.3 T9 發票、對帳與會計／稅務 draft 邊界

**來源識別**

- Repository：`pingoapple88/stallpay-v2`
- Branch：`feat/t9-p0-invoice-contract`
- Commit：`87bdde0be0f1e24a16cd093bcf232d4f336088c7`；該值來自 T9 evidence index，本次沒有獨立執行 repository 驗證。
- Contract：`T9-PAYMENT-ACCOUNTING-BOUNDARY-W1-0.1`、`T9-CONTRACT-HARNESS-W1-0.1` 與相鄰 `Contract v1.8`。
- 證據文件：`T9_PAYMENT_REFUND_RECONCILIATION_ACCOUNTING_BOUNDARY_v0.1.md`、`T9_CONTRACT_FIXTURE_HARNESS_v0.1.md`、`T9_R1_RUNTIME_GOVERNANCE_EVIDENCE_INDEX_2026-08-29.md`。

**分類：`EXTEND_VIA_ADAPTER`**

可參考的 provider-neutral 能力包括：

- `IInvoiceProvider` 作為發票抽象 port。
- `IReconciliationAdapter` 作為對帳抽象 port。
- `IAccountingProvider` 作為 accounting export draft port，而非正式申報 port。
- `amount_minor` 整數金額、currency、UTC、opaque reference、idempotency replay／payload conflict fail-closed、audit intent、redaction 與 server-principal company scope。
- unknown、manual review、no retry、no duplicate、blocked 與 synthetic harness 測試方法。

**校鮮集 mapping：**

- invoice request／result、payment／refund reference、settlement record、accounting envelope 與校鮮集事件 mapping：[TODO: 待人工確認]。
- 正式發票 provider、sandbox、資格、PII redaction、Adapter owner：[TODO: 待人工確認]。
- ERP authoritative source、settlement 來源、對帳鍵與差異處理 owner：[TODO: 待人工確認]。
- account mapping、export schema、核准流程與正式會計環境：[TODO: 待人工確認]。
- 稅務 classification、稅率、課稅別、申報期限、會計科目與法律責任：[TODO: 待人工確認]。

**測試證據限制：**

T9 文件記載 L0／L1 contract、unknown policy、同 key replay／conflict、redaction、tenant scope、RBAC、audit 與無第五事件等 PASS 結果，但本次只取得文件與 evidence index，沒有直接取得或重跑原始 stdout／stderr。這些結果只能作為「文件記載的 synthetic governance evidence」，不能作為校鮮集正式發票、正式會計、正式稅務或正式 ERP 通過證據。

**禁止直接重用：**不得帶入 T9 的正式 provider runtime、簽章／加密、key、正式發票號碼、正式買受人資料、正式 settlement、正式會計資料、正式 DB 或稅率／會計科目。校鮮集必須建立自己的 Adapter、mapping、fixture、sandbox 與 release gate。

## 五、校鮮集第一階段 synthetic journey

### 5.1 Journey 目標

第一階段只驗證校鮮集自身的資料流與治理邊界。它不驗證正式客戶、正式 ERP、正式付款、正式發票或正式設備。所有輸入、會員、商品、訂單、校點、金額、ERP response 與事件紀錄都使用校鮮集專屬 synthetic fixture。

### 5.2 流程

```text
來源訊息
→ OrderAI 解析草稿
→ 低信心／缺欄位／商品不明時人工覆核
→ 校鮮集人工確認
→ 校鮮集 ERP 待確認資料
→ Mock／blocked／isolated UAT
```

### 5.3 建議 synthetic fixture

| Fixture | 校鮮集專屬內容 | 必要限制 |
|---|---|---|
| `xj_order_source_message_001` | 一段不含真實個資的校鮮集測試訊息 | 不得使用萬佳鄉、雲鼎 ERP 或其他專案訊息 |
| `xj_order_parse_draft_001` | 解析草稿、候選商品、數量、confidence、缺欄位與 redaction 結果 | Product／SKU、價格、currency 與 threshold 均需標示版本或 TODO |
| `xj_human_review_001` | 校鮮集人工覆核者、決策、原因、audit reference 與 UTC 時間 | 覆核角色與權限模型需 owner 核准 |
| `xj_erp_pending_001` | 校鮮集 normalized ERP 待確認結果或 blocked response | 不得放入正式 endpoint、raw response、正式商品 ID 或 credential |
| `xj_uat_cases_001` | mock、blocked、timeout、缺 SKU、低信心、重複請求、mapping mismatch 與人工完成案例 | 所有案例需可重放、可追蹤、可清理，且不得連接正式環境 |

### 5.4 Synthetic journey 狀態與允許動作

| 階段 | 校鮮集狀態 | 可做動作 | 禁止動作 |
|---|---|---|---|
| 1 | `SOURCE_RECEIVED` | 保存 synthetic message reference 與 UTC 時間 | 不保存真實 PII；不直接建正式訂單 |
| 2 | `PARSE_DRAFT_CREATED` | 顯示候選商品、數量、confidence、缺欄位 | 不把草稿視為已確認訂單 |
| 3 | `HUMAN_REVIEW_REQUIRED` | 由授權測試角色補欄位或退回 | 不由模型自行補出未知商品、價格或校點 |
| 4 | `XJ_CONFIRMED` | 保存人工決策、原因、audit reference 與 fixture version | 不直接呼叫正式 ERP、付款或發票 |
| 5 | `ERP_PENDING` | 送入 blocked／mock／isolated UAT adapter，取得 normalized result | 不使用未核准 endpoint；不把 mock result 當正式入庫 |
| 6 | `UAT_ASSERTED` | 驗證 scope、idempotency、audit、PII redaction、unknown policy 與 mapping version | 不執行正式庫存扣減、付款、開發票、申報或設備控制 |

### 5.5 最小 synthetic UAT 情境

第一階段至少需要以下校鮮集專屬案例：

1. 解析成功，所有必要欄位完整。
2. confidence 低於校鮮集待確認閾值。
3. 商品候選不唯一。
4. 數量缺失或不符合格式。
5. 校點或 sales location 缺失。
6. 人工確認後產生一筆 `XJ_CONFIRMED` 草稿。
7. ERP adapter 為 `blocked`，且不得建立正式外部請求。
8. ERP mock 回覆缺 SKU。
9. ERP mock 回覆 timeout 或 unknown。
10. 相同 idempotency key 與相同 payload 重播。
11. 相同 idempotency key 與不同 payload 衝突。
12. 校鮮集 mapping version 不一致。
13. PII redaction 失敗，流程 fail-closed。
14. tenant／company／store scope 不一致，拒絕處理。
15. 人工覆核完成後產生完整 audit evidence。

每一案例都應記錄：fixture ID、contract version、source repository／commit、adapter mode、expected status、actual status、exit code、stdout／stderr 路徑、artifact SHA256、rollback reference 與 owner。

## 六、第一階段驗收與交付證據

目前本報告只完成需求與資產盤點，尚未執行校鮮集 synthetic UAT。正式進入下一階段前，應由 owner 核准以下資料：

- 校鮮集專屬 `OrderParseResult` contract 與版本。
- 校鮮集 canonical status enum 與 transition table。
- 校鮮集 company／store／sales location scope。
- 校鮮集產品／SKU／ERP mapping contract。
- 校鮮集 ERP authoritative repository、branch、commit 與 owner。
- 校鮮集 blocked／mock／HTTP Adapter 行為。
- 校鮮集人工覆核角色與高風險權限。
- 校鮮集 synthetic fixture manifest 與資料清理政策。
- 校鮮集 isolated UAT 環境與 evidence harness。
- 校鮮集 payment／invoice／tax／accounting 是否在第一階段排除。

在上述內容未核准前，校鮮集維持：

```text
formal_connections = false
formal_inventory_write = false
formal_payment = false
formal_invoice = false
formal_tax_filing = false
formal_device_control = false
release_gate = BLOCKED
```

## 七、下一步建議

下一步不是直接改寫正式產品，而是建立一份由 owner 回填的「校鮮集第一階段決策表」。建議先完成以下八個決策：

1. 正式產品定位與第一個試點客戶類型。
2. 第一階段啟用的 order sources。
3. OrderAI 輸入型態與人工覆核角色。
4. 校鮮集 ERP authoritative owner 與 mapping owner。
5. 第一階段是否完全排除付款、發票、稅務與設備控制。
6. company／store／sales location 的正式 scope。
7. synthetic UAT 的 fixture、harness 與 evidence owner。
8. `direct`、`dealer`、`enterprise` 方案是否於第一階段只做資料模型，尚不公開價格。

在 owner 完成上述決策前，任何共用能力只能作為方法與抽象設計參考，不可被寫成校鮮集正式整合承諾。

## 八、主權與隔離檢核

| 檢核項目 | 結果 | 說明 |
|---|---|---|
| 校鮮集與其他專案是否分開管理 | 通過 | 本報告只針對校鮮集 branch 與指定共用能力證據，未帶入其他專案客戶資料。 |
| 是否直接套用其他專案品牌、商品、門店或價格 | 通過 | 未套用；所有校鮮集未確認內容均標示 `[TODO: 待人工確認]`。 |
| 是否直接套用正式 ERP、支付、發票、稅務或設備 endpoint | 通過 | 未套用；正式 endpoint 與 owner 均列為 TODO。 |
| 是否把文件宣稱當成 runtime 測試通過 | 通過 | 已區分文件記載證據與本次未直接取得的 stdout／exit code。 |
| 是否保持 provider-neutral 邊界 | 通過 | 只把抽象 port、測試方法與治理方向列為候選資產。 |
| 是否建立正式產品程式碼 | 否 | 本次只有 Markdown 盤點文件，未寫正式產品程式碼。 |
| 是否符合資料主權與標準化交付要求 | 部分 | 盤點文件已保存於校鮮集 Git branch；正式資料庫、migration、部署 owner 尚未確認。 |

## References

[1]: ../projects/merchcore-stallpay-e5845ba0/WO-T5-ORDERAI-SELF-SERVICE-UI-WEEK1.md "OrderAI P1 UI 與交接工作單"

[2]: ../projects/merchcore-stallpay-e5845ba0/MerchCore跨模組事件契約差異矩陣v1.8(W2補正版).md "MerchCore 跨模組事件契約差異矩陣 v1.8"

[3]: ../projects/merchcore-stallpay-e5845ba0/WO-T8-ERP-INVENTORY-INTEGRATION-WEEK1.md "ERP 與庫存整合工作單"

[4]: ../projects/merchcore-stallpay-e5845ba0/T9_PAYMENT_REFUND_RECONCILIATION_ACCOUNTING_BOUNDARY_v0.1.md "T9 付款退款對帳會計邊界"

[5]: ../projects/merchcore-stallpay-e5845ba0/T9_CONTRACT_FIXTURE_HARNESS_v0.1.md "T9 Contract Fixture Harness"

[6]: ../projects/merchcore-stallpay-e5845ba0/T9_R1_RUNTIME_GOVERNANCE_EVIDENCE_INDEX_2026-08-29.md "T9 R1 Runtime Governance Evidence Index"

[7]: ./XIAOXIANJI_PREVIEW.md "校鮮集食品團購企業展示原型"

[8]: ./XIAOXIANJI_PRODUCTIZATION_ROADMAP.md "校鮮集從展示原型走向可銷售平台的產品化藍圖"

[9]: ./XIAOXIANJI_THERMAL_EXCEPTION_REMEDIATION.md "校鮮集三溫層無人取貨異常補救處理機制"

[10]: ./IMIN_F1_AND_SETTLEMENT_OPERATIONS.md "校鮮集 iMin F1 收銀與自動結算對帳操作說明"

## 文件邊界

本文件不代表正式公司名稱、正式產品規格、正式 ERP、正式付款、正式發票、正式稅務、正式會計、正式設備、正式客戶資料或正式商業成果。所有未確認資料均標示 `[TODO: 待人工確認]`。本文件沒有把萬佳鄉、雲鼎 ERP、StallPay 核心專案或其他專案的正式資料套用至校鮮集。

© 2026 JCINN 捷州資訊. Concept showcase.

§1 平台中立 · §2 原始碼主權 · §3 標準化部署 · §4 技術棧白名單 · §5 資料主權 · §6 AI 可替換 · §7 主權檢核
