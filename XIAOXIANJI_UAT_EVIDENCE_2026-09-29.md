# 校鮮集外部服務隔離 UAT 證據

**日期：**2026-09-29

## 測試入口規劃

- 永久展示站：`https://xiaoxianji.merchcore.ai/`
- 永久 UAT 展示：`https://xiaoxianji.merchcore.ai/uat/`
- 正式 API：`https://api.xiaoxianji.merchcore.ai/`
- Webhook：`https://webhook.xiaoxianji.merchcore.ai/`

DNS、TLS 與正式 API 主機在完成部署前標示 `[TODO: 待人工確認]`；測試證據不保存任何暫時執行環境網址。

## 自動測試

```text
32 passed
FULL_UAT_PASS
FULL_UAT_STRUCTURE_PASS
SKILL_UAT_PASS
```

HTTP smoke test 已完成：

```text
healthz → ok
物流 label → label_ready
Intella payment create → processing
有效 callback → paid
payment query → paid
formal_side_effects → false
```

## 瀏覽器互動測試

| 項目 | 結果 |
|---|---|
| 繁體中文介面 | 通過 |
| English 介面 | 通過 |
| ไทย 介面 | 通過 |
| 雲鼎物流測試標籤 | 回傳 `YD-SBX-*` 與 `label_ready` |
| Intella 測試付款 | 回傳 `INT-SBX-*` 與 `processing` |
| 錯誤簽章 | 回傳 `blocked`／`invalid_signature` |
| 有效成功通知 | 回傳 `paid` |
| 付款狀態查詢 | 維持 `paid` |

## 安全與資料邊界

- 只使用 synthetic UUID、訂單與金額。
- 未寫入正式客戶資料。
- 未配置 Intella 或雲鼎正式 credential。
- 未產生真實託運、扣款、退款、發票或撥款。
- Intella AES／RSA 與 callback 驗簽使用測試生成金鑰驗證，不包含任何正式 private key。
- `FORMAL_SERVICE_CONNECTED=false`。
