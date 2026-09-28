# 校鮮集 Demo 與正式後端基線對照報告

**檢視日期：** 2026-09-28

**Demo：** https://feat-xiaoxianji-enterprise-p.stallpay-lp.pages.dev/#device-sim

**正式後端基線：** `backend/`，commit `a90b6b64bdcebaaa368a73c9dcc9463ced103952`

## 1. 結論

公開頁面是清楚標示的食品團購企業展示原型，頁面使用 `DEMO MOCK`、`BENEFIT MOCK`、`SUCCESS MOCK`、`DEVICE MOCK`、`HARDWARE MOCK` 與合成數據標籤。它適合用來確認產品意圖、管理者視角、互動流程與待決策清單；不代表正式資料庫、付款、發票、ERP、LINE、設備或 LLM 已完成整合。

目前正式後端只建立治理與 Adapter 基線，沒有把 Demo 數字或跨專案正式資料帶入。

## 2. 模組對照

| Demo 模組 | Demo 證據 | 正式化分類 | 目前正式基線 | 尚需處理 |
|---|---|---|---|---|
| 多校／合作社管理 | 100 所展示校點、合作社與校點摘要 | `OWNER_DECISION_REQUIRED` | `organizations` scope 初始 migration | 法人、公司、合作社、校點與資料 owner |
| 會員／LINE 綁定 | 會員分群、LINE 綁定與通知偏好 | `ADAPTER_REQUIRED` | 尚未建立會員資料表或 LINE provider | PII、會員資格、LINE identity 與通知責任 |
| 商品／團購 | 合成 SKU、溫層、團購檔期與供應狀態 | `OWNER_DECISION_REQUIRED` | 尚無正式 product／SKU schema | SKU authority、價格規則、批次與效期 |
| 多校庫存 | 186 SKU、低庫存、調撥與溫層展示 | `ADAPTER_REQUIRED` | `IInventoryProvider` contract | ERP authority、reserve／deduct／reconcile semantics |
| 訂單／取貨 | 訂單狀態、配送批次、取貨編號 | `ADAPTER_REQUIRED` | 尚無正式 order schema | 訂單 owner、來源 contract、idempotency |
| ERP 財務對帳 | 應收、已收、待核對與 fail-closed 概念 | `ADAPTER_REQUIRED` | `IInvoiceProvider`、`IERPProvider` contract；audit baseline | 付款、發票、會計、稅務 owner 與 reconciliation contract |
| 福利點數／回饋金 | 福利批次、點數、回饋、退貨沖正展示 | `OWNER_DECISION_REQUIRED` | 尚無 loyalty ledger | 合作社核准、資格、規則版本與正式帳本 |
| OrderAI 成功資料流 | LINE 訊息→確認→庫存→取貨→ERP 對帳 | `ADAPTER_REQUIRED` | `ILLMProvider` contract、governance endpoint | OrderParseResult、confidence、人工覆核與 ERP mapping |
| iMin F1 | 掃碼、金額確認、展示發票列印 | `DEMO_ONLY` + `ADAPTER_REQUIRED` | `IInvoiceProvider` contract | 正式型號、SDK、發票資格、付款結果與稅務責任 |
| 智販機／取物櫃 | QR、取貨碼、設備回報與狀態回寫 | `ADAPTER_REQUIRED` | `IDeviceProvider` contract | 設備 owner、API、韌體、開櫃協議與 SLA |
| 設備異常 LINE 通知 | 低庫存、盤點差異、溫度異常、補貨任務 | `ADAPTER_REQUIRED` | `INotificationProvider` contract | EventBus、供應商補貨、接收者、通知 SLA |
| 三溫層異常補救 | 開門失敗、結果不明、物品未取出、溫層不明 | `FORMAL_BASELINE` 候選流程 | 邊界文件已要求 fail-closed | 設備事件 contract、人工角色、替代取貨與 audit |

## 3. Demo 明確宣告的限制

頁面已明確說明：

- 100 所、會員、訂單、庫存、金額與對帳數字是展示／合成資料。
- 不會建立正式訂單或收集付款資料。
- 不會真的發送 LINE 通知。
- 不會實際開門、修改庫存或完成正式訂單。
- iMin 發票是靜態樣張，不具正式憑證效力。
- 正式 ERP、付款、發票、LINE、設備、SDK、韌體與 LLM 接點待確認。

這些限制與 `PROJECT_BOUNDARY.md` 及後端的 `FORMAL_SERVICE_CONNECTED=false` 一致。

## 4. 正式後端目前已完成

- FastAPI `/healthz`。
- `/api/v1/governance/status`，預設回報外部整合 blocked。
- LLM、ERP、庫存、發票、付款、設備、通知 Adapter contracts。
- PostgreSQL `organizations` 初始 scope。
- append-only `audit_logs` migration。
- Dockerfile、docker-compose、`.env.example`。
- 2 個 smoke tests 通過。

## 5. 主要差距

### 5.1 資料模型差距

Demo 顯示的會員、商品、訂單、庫存、設備與福利資料，目前均未進入正式 schema。下一階段應先由 owner 核准：

- organization／company／store／sales location scope。
- product／SKU authority。
- inventory authority。
- order source 與 order owner。
- supplier／device／cooperative relationship。

### 5.2 財務與稅務差距

Demo 的金額只能作畫面與流程示意。正式化前仍不能推定：

- 誰收款。
- 誰開發票。
- 誰負責退款、折讓與申報。
- 會計／稅務資料由誰核准。
- 福利回饋與點數是否屬會員福利、合作社服務或其他安排。

### 5.3 設備與補貨差距

Demo 可以模擬設備事件，但正式化需要：

- `device_id` 與設備所有權。
- 設備是只取貨或直接銷售。
- 供應商自行補貨資格與授權範圍。
- 補貨驗收、盤點差異、報廢、溫層與效期責任。
- 設備 API、韌體、網路、開門結果與維修 SLA。

### 5.4 OrderAI 差距

Demo 的成功流程與低信心流程是產品意圖證據，不是正式 OrderAI contract。正式化前需要校鮮集專屬：

- input／output schema。
- confidence 與 reason codes。
- 人工覆核角色與 RBAC。
- 商品／SKU matching。
- 會員／校點 scope。
- ERP delivery、retry、dead-letter 與 audit semantics。

## 6. 建議下一個開發批次

1. 核准 organization、company、cooperative、school、device、supplier 的 scope 與 RBAC。
2. 建立校鮮集專屬 domain contracts 與 synthetic fixtures。
3. 建立 supplier self-restock、device inventory 與 settlement rule models。
4. 建立 OrderAI `needs_human_review` 的校鮮集 mapping，不引用其他專案正式 schema。
5. 建立 blocked／mock ERP ingest 與 reconciliation harness。
6. 為每一條 Demo 流程建立對應的 API contract、audit event 與 fail-closed test。
7. owner 核准後，才進行正式 provider implementation 與 isolated UAT。

## 7. 判定

目前 Demo 與正式後端沒有矛盾：

- Demo 負責產品展示與互動概念。
- `PROJECT_BOUNDARY.md` 負責專案隔離與正式治理。
- `backend/` 負責正式產品的 provider-neutral 開發起點。
- 所有外部整合仍維持 blocked，直到完成 owner、contract、資料主權與測試 gate。
