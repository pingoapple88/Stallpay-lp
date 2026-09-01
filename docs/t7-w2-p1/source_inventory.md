# WO-T7-W2-P1 來源清冊（去敏）

| Source ID | 檔名／類型 | SHA-256／metadata | 用途 | Git 處置 |
|---|---|---|---|---|
| `SRC-WO-01` | `WO-T7-W2-P1｜天來APIv2.7唯讀Mapping與設備異常FaultHarness`／Markdown | 使用者提供；內容已轉錄於本工單執行上下文 | 工作範圍、禁止項目、交付與驗收 | 不重複提交原附件 |
| `SRC-TIANLAI-PDF-01` | `天來集團_條碼API串接_即時預訂20251209.pdf`／PDF | SHA-256=`76da3e56811c37be228639b8a8646cc6bb8398805571cf55cfd1739e07e4ce5a`；建立時間 2025-12-09T17:13:16Z；24 頁 | 候選 endpoint／參數／回應材料 | 供應商原檔不提交 Git，只記錄 hash 與判定 |
| `SRC-TIANLAI-Q-01` | `天來APIQ.docx`／Word | 共享文件；內容提及現有文件為 `v2.5` | 版本、環境、scope、設備與帳務待確認問題 | 原檔不提交 Git，只保留去敏判定 |
| `SRC-CLIENT-01` | 既有 `tenlifeClient.ts` | `pingoapple88/stallpay-v2@f883fa9e617b41e8e0885ad821975f56bb6ae99f` | 三支候選 read-only client 方法與 error handling | 僅讀取、不修改 |
| `SRC-PROVIDER-01` | 既有 `vendingMachineProvider.ts`／`tenlifeVendingProvider.ts` | 同上 revision | T2 Adapter 消費邊界與現有 `getProducts` gap | 僅讀取、不修改 |

> 清冊不包含 Token、company 明文、簽章、完整 request URL、response body、PII 或正式設備資料。供應商 PDF 與問答原檔不隨本輪交付提交至 Git。
