
## 第八開發批次：可操作的隔離 UAT

新增雲鼎物流 synthetic sandbox provider 與 Intella Scan2Pay contract-level sandbox provider，並提供以下 API：

```text
POST /api/v1/uat/logistics/labels
POST /api/v1/uat/payments
GET  /api/v1/uat/payments/{payment_reference}
POST /api/v1/uat/payments/{payment_reference}/callback
```

所有 UAT API 必須帶 `X-UAT-Mode: isolated`。三語操作台位於 `/uat/`，API 文件位於 `/docs`。可使用 `python3 scripts/uat_smoke.py http://127.0.0.1:8000` 跑完整物流標籤、付款建立、callback 與狀態查詢流程。

目前 Intella provider 依公開文件驗證 order reference、minor-unit 金額、processing／paid／failed 狀態與簽章 fail-closed；`app/adapters/intella_crypto.py` 已實作 AES-128-CBC、RSA PKCS#1 v1.5 request envelope、response 解密與 SHA-256 callback 驗簽，並使用測試生成金鑰驗證。真正 sandbox HTTP 呼叫仍需 Intella 發放測試 server URL、merchant ID、public key、AES IV 與交易密碼。雲鼎物流尚無核准的公開 contract，因此維持 `ILogisticsProvider` synthetic adapter。
