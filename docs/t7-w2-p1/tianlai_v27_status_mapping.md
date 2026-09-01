# 天來 API v2.7 唯讀 Status Mapping

| 文件欄位 | 值 |
|---|---|
| Work Order | `WO-T7-W2-P1` |
| 版本 | `T7-TIANLAI-V27-READONLY-STATUS-01` |
| 模式 | `SYNTHETIC_FAULT_HARNESS` |
| 正式文件狀態 | `BLOCKED_BY_ENDPOINT_SCHEMA` |
| 正式 API 執行 | 未執行 |

> 現有候選 client 將外層 `state === 0` 視為 API 成功、`state !== 0` 視為 API error，並對非 2xx 與非 JSON 回應分別拋出 HTTP／API error；但 v2.7 第 10 節權威文件尚未取得，故此映射只供 T2 的 synthetic Adapter 設計與測試，不是天來正式錯誤碼表。[1] [2]

## 一、Raw → Canonical 狀態映射

| Scenario | Raw 條件 | Canonical status | Retryable | Reconciliation／manual review | T2 處置 |
|---|---|---|---:|---:|---|
| `success` | HTTP 2xx、JSON、`state=0`、必要陣列與欄位完整且 scope 一致 | `success` | false | false | 產生去敏 canonical mapping |
| `empty_data` | HTTP 2xx、JSON、`state=0`、資料陣列為 `[]` | `empty` | false | false | 回空集合，不偽造資料 |
| `http_error` | HTTP 非 2xx | `error` | `[TODO: 待人工確認]` | true | 不解析 body 為可操作資料；保存去敏 HTTP metadata |
| `api_error` | HTTP 2xx、JSON、`state != 0` | `blocked` | false | true | 保留 `state`，遮罩 `message`，禁止回傳 mapping |
| `timeout` | 受控 timeout | `unknown` | false | true | 不自動重送；要求受控 status check／人工確認 |
| `malformed_json` | 回應不是有效 JSON | `blocked` | false | true | fail-closed；不保存完整 upstream body |
| `missing_required_field` | 必要頂層／item 欄位缺失 | `blocked` | false | true | 標 `BLOCKED_BY_ENDPOINT_SCHEMA`，不填預設值 |
| `invalid_machine` | machine code 不存在或 API 明確拒絕 | `blocked` | false | true | 不建立 machine mapping |
| `invalid_commodity` | commodity code／ID 不存在或不在核准範圍 | `blocked` | false | true | 不建立 commodity mapping |
| `mapping_conflict` | 同一 machine＋layer 對到多個商品、或 commodity ID／code 衝突 | `manual_review` | false | true | 不自動選一筆；產生 mapping discrepancy |
| `scope_mismatch` | company、machine、commodity 任一不屬於 server principal | `blocked` | false | true | fail-closed；建立資安 audit reference |
| `unknown_state` | 未知 `state` 或 message 語意不明 | `unknown` | false | true | 要求 API owner 確認，不重試、不猜測 |

## 二、必要欄位驗證

| Endpoint | 必要頂層欄位 | 必要 item 欄位 | 缺欄位處置 |
|---|---|---|---|
| Machine | `state`、`message`、`machine` | 候選：`code`、`name`；`user`、`qty`、module 欄位正式必填性 `[TODO]` | `blocked`／`BLOCKED_BY_ENDPOINT_SCHEMA` |
| Commodity | `state`、`message`、`commodity` | 候選：`commodityID`、`commodityCode`、`commodityName`、`price`；`stop` 正式必填性 `[TODO]` | `blocked`／不輸出商品 |
| MachineCommodity | `state`、`message`、`commodity` | 候選：`layer`、`commodityID`、`commodityCode`；`shelflife` 可空性 `[TODO]` | `blocked`／不輸出 mapping |

## 三、Scope 與 Mapping 不變條件

| 不變條件 | 結果 |
|---|---|
| company 必須由 server principal／受控 credential context 決定 | 不能接受 fixture 或使用者輸入覆蓋正式 company scope |
| machine 必須存在於同一 company 的 Machine 清單 | 不存在即 `invalid_machine` |
| commodity ID 與 code 必須在同一 company 的 Commodity 清單中互相一致 | 不一致即 `mapping_conflict` |
| MachineCommodity 的每一筆 machine＋layer 在同一 snapshot 只能有一個有效商品 | 多值即 `mapping_conflict` |
| 任何 scope mismatch 不得回傳可供控制流程使用的資料 | `blocked`＋audit reference |
| 空資料不等同 error，也不等同有庫存 | `empty` |
| `state=0` 只代表候選 API 外層成功，不代表 mapping 已獲 owner 核准 | 保留 evidence level=`MOCK`／`READ_ONLY_DISCOVERY` |

## 四、錯誤輸出 contract

```json
{
  "status": "blocked",
  "error": {
    "code": "TIANLAI_SCOPE_MISMATCH",
    "category": "scope",
    "retryable": false,
    "requires_reconciliation_or_manual_review": true,
    "message_key": "vending.mapping.scope_mismatch"
  },
  "upstream": {
    "http_status": 200,
    "state": 0,
    "message_redacted": true,
    "raw_body_persisted": false
  },
  "mode": "SYNTHETIC_FAULT_HARNESS",
  "formal_mapping_verified": false,
  "gate_06": "BLOCKED"
}
```

## 五、安全規則

所有 fixture 與 log 不得包含 Token、簽章值、完整 URL、真實 company code、真實 machine／commodity 識別、PII 或未遮罩 upstream body。`timeout`、未知 state、mapping conflict 與 scope mismatch 均不得自動重送或選擇預設 mapping。T7 不開門、不出貨、不退款，也不修改 ERP 正式庫存。

## References

[1]: ./tianlai_v27_document_and_request_contract.md "天來 API v2.7 文件核對與唯讀 Request Contract"
[2]: https://github.com/pingoapple88/stallpay-v2/blob/f883fa9e617b41e8e0885ad821975f56bb6ae99f/server/vending/providers/tenlife/tenlifeClient.ts "既有 Tenlife client 候選錯誤處理"
[3]: ./source_inventory.md "WO-T7-W2-P1 去敏來源清冊"
