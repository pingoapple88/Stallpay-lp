# 校鮮集專案邊界

**文件版本：** v1.0
**最後更新：** 2026-09-28
**文件性質：** 正式開發前置治理文件；不是法律、會計、稅務意見或正式產品規格。

## 1. 專案定位

校鮮集是獨立的企業產品專案，暫定涵蓋多校團購、學校／機關、軍公教、職工福利合作社、智販機與取貨設備的營運管理。正式產品定位、法人、營業主體、服務範圍與對外承諾，均須由校鮮集 owner 核准。

未核准事項一律標示 `[TODO: 待人工確認]`，不得由其他專案、原型畫面或口頭假設推定。

## 2. 校鮮集專屬範圍

本專案可自行定義與驗證：

- 學校、機關、軍公教團購與職工福利合作社的組織 scope。
- 校鮮集專屬會員、團購檔期、商品／SKU、訂單、配送、取貨與多校庫存。
- 智販機／取物櫃「只作取貨」與「直接銷售」兩種模式。
- OrderAI 人工覆核、人工確認角色與 fail-closed 流程。
- 動態價格、點數、回饋、供應商自行補貨、分潤與結算規則。
- 校鮮集專屬 Adapter、EventBus、audit、synthetic fixture、UAT 與部署設定。

所有金額、比例、含稅／未稅方式、結算週期、門檻與設備規則，必須是版本化、可啟用／停用、可設定有效期且可追溯的規則，禁止寫死。

## 3. 尚未核准的正式事項

- 正式產品定位、法人／品牌／營業主體與組織階層。
- 學校、機關、合作社、供應商、平台與設備的責任歸屬。
- 訂單來源：LINE、Web、POS、團購、CSV、人工輸入或其他來源。
- OrderAI 輸入型態、解析契約、confidence 閾值與人工覆核角色。
- 商品／SKU authority、庫存 authority、ERP authority 與 mapping owner。
- 付款、退款、發票、會計、稅務申報與薪資責任。
- 智販機的銷售、收款、發票、庫存、補貨、維修與分潤主體。
- 供應商自行補貨資格、可補貨設備、補貨驗收、庫存責任與結算規則。
- `direct`、`dealer`、`enterprise` 方案、價格版本、服務內容與經銷分潤。
- 正式資料庫、網域、部署 owner、監控、備份、災難復原與事件通報。

核准前只能使用 `blocked`、`mock`、`pending_owner_decision` 或 `manual_review_required`，不得自動完成正式交易、申報或撥款。

## 4. 禁止直接引用的資料範圍

不得從萬佳鄉、雲鼎 ERP、捷州 ERP、StallPay 核心專案或其他 repository 直接帶入：

### 4.1 業務與客戶資料

- 客戶、會員、員工、學校、機關、合作社、門店、加盟點與供應商資料。
- 品牌名稱、文案、商品、SKU、商品 ID、價格、促銷與庫存數字。
- 客戶合約、加盟條款、服務費、加盟費、佣金、分潤比例與結算週期。

### 4.2 技術與正式整合資料

- 正式 endpoint、URL、service ID、tenant ID、company ID、store ID、sales location ID。
- API Key、OAuth Secret、HMAC Secret、憑證、cookie、token、帳號與任何 credential。
- 正式資料庫連線、migration、schema、raw payload、正式 mapping 與資料保留政策。
- 正式付款、發票、稅務、會計、薪資、ERP、LINE、設備或申報連線設定。
- 其他專案正式程式碼、測試資料、fixture、部署設定與 production runbook。

### 4.3 法規與財務判定

- 稅率、課稅別、申報期限、會計科目、發票責任與所得／營業稅判定。
- 其他專案已核准的退款、折讓、點數、福利、分潤或薪資規則。

## 5. 可參考但不得直接複製

只能參考 provider-neutral 方法，並在校鮮集重新建立 contract、mapping、fixture 與測試：

- OrderAI 低信心、缺欄位、商品不明的人工覆核狀態模式。
- ERP ingest、商品 mapping、reserve／release／deduct／reconcile 抽象介面。
- 發票、對帳、會計 draft 的 provider-neutral port。
- `company_id`、`organization_id`、`store_id`、`sales_location_id` 的 scope 方法。
- idempotency、audit、UTC、minor units、PII 加密／遮罩、fail-closed。
- Adapter、EventBus、synthetic fixture、isolated UAT 與 evidence harness。

任何採用必須記錄：

```text
來源 repository：
來源 branch：
來源 commit：
contract 版本：
測試證據：
校鮮集客製 mapping：
校鮮集 owner 核准：
```

未完成紀錄與核准前，能力維持 `NEEDS_OWNER_DECISION` 或 `BLOCKED`。

## 6. 正式開發基線

- Production 使用 Python FastAPI、SQLAlchemy、PostgreSQL 與 migration。
- 外部服務全部透過介面隔離：`ILLMProvider`、`IPaymentProvider`、`IInvoiceProvider`、`IAccountingProvider`、`IERPProvider`、`IInventoryProvider`、`IDeviceProvider`、`INotificationProvider`。
- 每個 API 第一行執行認證／RBAC；查詢必須帶合法 organization／company scope。
- 狀態變更寫入 append-only `audit_logs`，包含 actor、scope、事件、前後狀態、idempotency reference 與 UTC。
- 金額使用整數 minor units；PII 使用加密／遮罩；時間統一 UTC。
- 規則未命中、外部結果不明、設備結果不明、付款／發票狀態不明時 fail-closed。
- API Key、閾值、比例、金額、含稅／未稅方式、結算週期與 endpoint 全部外部化或版本化規則。
- UI 與訊息內容走 i18n，租戶設定可 override，但不得突破權限與稽核限制。

## 7. 資料與部署主權

正式資料只能存放於校鮮集 owner 核准的自有基礎設施，例如 Railway 或其他核准環境。展示原型、synthetic fixture 與 mock 資料不得當作正式客戶資料。

正式環境、測試環境、UAT 與展示環境必須分離。正式部署需提供 Dockerfile、docker-compose、`.env.example`、migration、health check、備份／還原說明。

## 8. 跨 Chat／repository 變更規則

1. 先記錄來源與版本。
2. 完成專案隔離檢查。
3. 重新命名與 mapping contract 欄位。
4. 建立校鮮集 synthetic fixture 與 focused tests。
5. 取得 owner 核准並寫入 audit／變更紀錄。
6. 覆蓋失敗、timeout、重送、部分成功與人工介入情境。

禁止以「其他專案已經可以用」作為校鮮集正式採用理由。

## 9. 邊界 owner

| 責任 | 校鮮集 owner |
|---|---|
| 產品範圍與對外承諾 | `[TODO: 待人工確認]` |
| 法人／營業主體 | `[TODO: 待人工確認]` |
| 商品／SKU authority | `[TODO: 待人工確認]` |
| 庫存與 ERP authority | `[TODO: 待人工確認]` |
| 付款與退款 | `[TODO: 待人工確認]` |
| 發票／會計／稅務 | `[TODO: 待人工確認]` |
| 智販機與供應商補貨 | `[TODO: 待人工確認]` |
| 資料保護與 PII | `[TODO: 待人工確認]` |
| 正式部署與維運 | `[TODO: 待人工確認]` |
| 跨專案能力核准 | `[TODO: 待人工確認]` |

## 10. 主權檢核

1. 平台中立：外部服務透過 Adapter，無特定 AI 平台 runtime dependency。
2. 原始碼主權：產出可提交至 Jiimoo／pingoapple88 Git。
3. 標準化部署：提供 Dockerfile、docker-compose、`.env.example` 與 migration。
4. 技術白名單：正式後端使用 Python FastAPI、SQLAlchemy、PostgreSQL。
5. 資料主權：正式資料僅流向 owner 核准的自有基礎設施。
6. AI 可替換：LLM 透過 `ILLMProvider` 並可切換 provider。
7. 強制檢核：交付前逐項記錄，任一否決先修正。

本文件若與其他專案文件衝突，以校鮮集 owner 最新核准版本為準，但不得違反集團主權守則與技術治理框架。
