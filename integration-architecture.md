# StallPay 多國語言、ERP 與經銷商整合架構規劃

本文件依據 Jiimoo 集團「雙層治理規範」與「雙價位 DNA」原則，規劃 StallPay 產品線在多國語言（i18n）、MerchCore ERP 整合，以及經銷商體系（L1~L4）的系統架構與實作路徑。

## 1. 系統架構全景

StallPay 的系統架構設計遵循「平台中立」與「事件驅動」原則，將前端展示、中介層與核心 ERP 分離。

*   **前端（dealer-portal & stallpay-v2）**：純 UI 展示層，包含經銷商後台與攤主操作介面。負責處理多國語言切換與使用者互動。
*   **中介層（StallPay Backend API）**：負責處理專屬於 StallPay 的業務邏輯（如 LINE LIFF 登入驗證、推薦碼生成、特定報表），並作為前端與 ERP 之間的橋樑。
*   **核心層（MerchCore ERP）**：作為 Single Source of Truth，集中管理跨產品線的共用資料，包含夥伴層級、分潤計算、撥款紀錄與晉升條件設定。

## 2. 多國語言（i18n）基礎建設

為符合集團規範，StallPay 前端必須具備支援繁體中文（zh-TW）、英文（en）與泰文（th）的能力。

### 2.1 實作方案
*   **技術選型**：採用 `react-i18next` 搭配 `i18next`。
*   **資源管理**：語言檔以 JSON 格式儲存，依語系分類（例：`locales/zh-TW/common.json`）。
*   **切換機制**：於 Header 提供語言切換選單，使用者選擇後將偏好存入 `localStorage`。預設語言依瀏覽器設定判斷，若無對應語言則 fallback 至 `zh-TW`。

### 2.2 容錯機制
實作多語系時，必須加入 Fallback 機制，避免因缺少翻譯 Key 導致畫面空白或錯誤。
```javascript
// 建議的翻譯函式封裝概念
const t = (key, lang = currentLang) => { 
  return translations[lang]?.[key] ?? translations['en']?.[key] ?? key; 
};
```

## 3. MerchCore ERP 整合策略

dealer-portal 嚴禁直接連線至 ERP 資料庫或呼叫 ERP 內部 API，所有資料交換必須透過 StallPay 中介層 API 進行。

### 3.1 資料同步流向

| 資料項目 | 資料來源 | 同步 / 存取方式 |
| :--- | :--- | :--- |
| **夥伴基本資料 (Name, Level)** | ERP 夥伴模組 | 登入時由 StallPay API 向 ERP 查詢並快取 |
| **晉升條件門檻** | ERP 設定模組 | StallPay API 定期讀取或即時查詢 |
| **分潤明細與預估** | ERP 分潤計算模組 | 批次同步（例如每月 15 日）至 StallPay |
| **撥款紀錄** | ERP 撥款模組 | 撥款完成後，透過 EventBus 推送至 StallPay |
| **攤主清單與推薦碼** | StallPay 中介層 | StallPay 自有資料，不需同步至 ERP |

### 3.2 整合介面需求 (給 CC 的開發參考)
StallPay 中介層需要向 ERP 請求以下 API 介面（由 ERP 提供）：
*   `GET /internal/erp/partners/{openId}`：查詢夥伴層級與基本狀態。
*   `GET /internal/erp/commissions?partnerId={id}&month={YYYY-MM}`：查詢特定月份的分潤明細。
*   `GET /internal/erp/settings/upgrade-rules`：取得最新的晉升條件設定。

## 4. L1~L4 經銷商體系與晉升機制

### 4.1 權限與 UI 呈現
`dealer-portal` 採用單一 SPA 架構，依據 `user.level` 動態渲染可見區塊。
*   **L1**：著重於推薦碼管理、我的客戶清單與個人分潤明細。
*   **L2~L4**：除 L1 功能外，增加「我的團隊」與對應層級的業績報表。L4 可見全國總覽。

### 4.2 晉升條件動態化
晉升條件（如所需攤主數、下線夥伴數）不可寫死於前端程式碼，必須由總後台（Admin Panel）設定，並存於 ERP 中。

*   **前端呈現**：透過呼叫 `GET /api/dealer/upgrade-progress`，取得目前進度與目標門檻，渲染進度條元件。
*   **兼任與跳級**：允許高層級夥伴向下兼任（例如 L4 仍可直接推廣攤主）。允許透過人工審核進行跳級晉升。

## 5. 後續實作建議

1.  **P0**：完成前端 `ProfileSetupModal`（首次登入對話框），讓登入與註冊流程跑通。
2.  **P1**：於 `dealer-portal` 導入 `react-i18next` 基礎架構。
3.  **P2**：由 CC 團隊建立 StallPay 後端 API，並與 ERP 進行初步串接（如取得夥伴層級）。
4.  **P3**：實作晉升進度條與分潤明細頁面。
