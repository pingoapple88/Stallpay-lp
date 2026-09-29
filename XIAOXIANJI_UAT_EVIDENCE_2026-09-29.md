# 校鮮集外部服務隔離 UAT 證據

**日期：**2026-09-29

## 公開測試入口

- UAT 操作台：https://8000-iy8a7lenenif4u7y0uco9-d963da66.sg2.manus.computer/uat/
- OpenAPI 文件：https://8000-iy8a7lenenif4u7y0uco9-d963da66.sg2.manus.computer/docs
- 健康檢查：https://8000-iy8a7lenenif4u7y0uco9-d963da66.sg2.manus.computer/healthz

以上網址是目前 Sandbox 暫時測試入口，不是 `xiaoxianji.merchcore.ai` 正式環境。

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
