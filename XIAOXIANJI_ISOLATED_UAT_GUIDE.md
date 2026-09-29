# 校鮮集外部服務隔離 UAT 指南

**版本日期：**2026-09-29

## 測試邊界

本 UAT 只使用 synthetic organization、訂單、託運單與付款資料。雲鼎物流與 Intella 都由校鮮集內建 sandbox provider 模擬，不會呼叫正式服務、不產生真實託運、不扣款、不退款、不開票。

## 本機啟動

```bash
cd backend
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

瀏覽器開啟：

```text
http://127.0.0.1:8000/uat/
```

API 文件：

```text
http://127.0.0.1:8000/docs
```

## 自動化 smoke test

```bash
cd backend
python3 scripts/uat_smoke.py http://127.0.0.1:8000
```

成功條件：物流回傳 `label_ready`，付款先回傳 `processing`，簽章有效的成功通知後查詢為 `paid`，所有 response 都維持 `formal_side_effects=false`。

## 人工測試順序

1. 在 UAT 操作台切換繁體中文、English、ไทย，確認文案切換。
2. 建立雲鼎物流測試標籤，確認 reference 以 `YD-SBX-` 開頭。
3. 建立 Intella 測試付款，確認狀態為 `processing`。
4. 先模擬錯誤簽章，確認結果為 `blocked`。
5. 再以新訂單模擬有效成功通知，確認狀態變成 `paid`。
6. 查詢付款狀態，確認 organization scope 一致且沒有正式 side effect。

## Intella 正式 sandbox 前置條件

依 Intella 公開 Scan2Pay 文件，需要向業務取得測試特店資料、API server URL、RSA public key 與 AES IV。官方文件說明 API 使用 TLS 1.2 以上、Request 以 AES-128-CBC 加密、AES key 以 RSA public key 加密；交易通知須以測試或正式環境對應 public key 驗證 SHA-256 簽章。

目前 `app/adapters/intella_crypto.py` 已完成上述加密 envelope、response 解密與 callback 驗簽元件，並以測試生成金鑰通過自動化測試；取得 Intella 發放的測試資料後，即可進一步接上真實 sandbox HTTP endpoint。

正式 sandbox 值只能放入核准的 Secret Manager／Railway Variables，不能提交 Git：

```text
INTELLA_API_BASE_URL
INTELLA_MERCHANT_ID
INTELLA_PUBLIC_KEY
INTELLA_AES_IV
INTELLA_TRANSACTION_PASSWORD
INTELLA_REFUND_PASSWORD
```

## 雲鼎物流正式 sandbox 前置條件

目前未取得校鮮集專屬的雲鼎物流 API contract、sandbox endpoint、credential、label format 或 webhook 規格，因此本 UAT 只驗證 `ILogisticsProvider` contract。正式接入前需由 owner 提供或核准上述資料，並完成 timeout、重送、亂序、取消、標籤失敗與 scope mismatch 測試。

## 公開參考

- Intella Scan2Pay API：https://intella.gitbook.io/scan2pay/master
- Intella API 環境：https://intella.gitbook.io/scan2pay/api-general-rules/api-environment
- Intella OLPay：https://intella.gitbook.io/scan2pay/api-specification/customer-scan
- Intella 交易結果通知：https://intella.gitbook.io/scan2pay/api-callback
- Intella 資料加解密：https://intella.gitbook.io/scan2pay/api-general-rules/api-jia-jie-mi-ming
