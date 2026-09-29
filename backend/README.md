
## 第七開發批次：Production 外部服務 readiness

新增 `ExternalIntegrationRegistration` 與 `/api/v1/mock/integrations/readiness`，用來檢查外部物流、金流、發票、ERP 或通知服務是否具備進入下一階段的條件。

Production 必須同時具備 production-ready status、owner approval reference、credential reference name、webhook path、idempotency support 與 sandbox evidence；本批次只檢查條件，不啟用正式連線，也不讀取或保存 secret value。

建議先驗證物流 sandbox，再進行金流 sandbox。完整 gate 與 owner 決策清單見根目錄 `XIAOXIANJI_PRODUCTION_EXTERNAL_INTEGRATION_PLAN.md`。
