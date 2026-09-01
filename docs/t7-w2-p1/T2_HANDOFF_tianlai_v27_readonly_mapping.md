# T2 Handoff｜天來 v2.7 唯讀 Mapping Canonical Input

| 欄位 | 值 |
|---|---|
| Work Order | `WO-T7-W2-P1` |
| 交接狀態 | `SYNTHETIC_CANONICAL_INPUT_READY` |
| 正式 discovery 狀態 | `BLOCKED_BY_ENDPOINT_SCHEMA` |
| Consumer | T2／`IVendingMachineProvider` Adapter 實作者 |
| Mode | `SYNTHETIC_FAULT_HARNESS` |
| Evidence level | `MOCK` |
| GATE-06 | `BLOCKED／TEST_DEVICE_REQUIRED` |

> **T2 消費原則：**只消費已列名欄位、canonical status 與 synthetic fault 期望值。fixture 內的 company、machine、commodity、layer 與價格均是合成資料，不得寫入正式資料庫、不得當成供應商核准 mapping，也不得用於設備控制。[1] [2]

## 一、交接檔案

| 檔案 | 用途 | 狀態 |
|---|---|---|
| `fixtures/machine_mapping_fixture.json` | machine code／name／company scope 與 9 個 fault cases | `READY_SYNTHETIC` |
| `fixtures/commodity_mapping_fixture.json` | commodity ID／code／name／原生元與 minor units 轉換、9 個 fault cases | `READY_SYNTHETIC` |
| `fixtures/machine_commodity_mapping_fixture.json` | machine＋commodity＋layer 關聯與 11 個 fault cases | `READY_SYNTHETIC` |
| `tianlai_v27_status_mapping.md` | raw HTTP／state／message／empty／malformed／scope 的 canonical mapping | `READY_SYNTHETIC` |
| `tianlai_v27_readback.json` | machine-readable 執行狀態、hash、Gate、TODO 與 next action | `READY` |
| `evidence/tianlai_v27_fault_harness.log` | 既有 client 的三個唯讀端點與 error handling focused run | `8 PASS／0 FAIL` |
| `evidence/tianlai_v27_device_fault_harness.log` | generic device fault runner | `10 scenarios／0 failures` |
| `evidence/tianlai_v27_mapping_fixture_validation.log` | JSON、coverage、redaction、hash 驗證 | `PASS` |

## 二、既有 Provider 差距

目前品牌中立介面只提供 `getProducts`、`getSales`、`getStatus`、`pushAd` 與 `setCoupon`，尚無 machine↔commodity mapping 的明確輸出型別。[3] Tenlife client 已有 `getMachines`、`getCommodities` 與 `getMachineCommodities` 候選方法，但 provider wrapper 的 `getProducts` 仍固定回空陣列，且註解與現有 client 能力不一致。[4] [5]

T2 應透過既有 `IVendingMachineProvider` 的 additive Adapter／read model 處理，不得新增第二套 StallPay core、schema、migration 或設備控制介面。若修改共享 interface，必須由該 interface owner 另行核准。

## 三、Canonical 欄位

| 類別 | 可消費欄位 | 暫不可假設 |
|---|---|---|
| Machine | `machine_code`、`machine_id`、`name`、`company_ref`、`source_updated_at_utc` | module／櫃型、qty、線上狀態與正式 ID 必填性 |
| Commodity | `commodity_id`、`commodity_code`、`name`、`price_native`、`price_native_unit`、`price_minor`、`status`、`company_ref` | image／category／vip／clear／stop 的正式語意與必填性 |
| MachineCommodity | `machine_code`、`commodity_id`、`commodity_code`、`slot_or_layer`、`shelflife_source` | layer 格式、格位容量、實際庫存量與 shelflife 可空性 |
| Error | `code`、`category`、`retryable`、`requires_reconciliation_or_manual_review`、`message_key` | 天來正式 fault code 與 retry policy |

金額必須在 Adapter 內把候選原生整數「元」轉為 integer minor units。時間若來源未帶時區，T2 不得自行假設；本輪 `source_updated_at_utc` 保留 `[TODO: 待人工確認]`。

## 四、必須 fail-closed 的情況

| 條件 | Canonical 結果 |
|---|---|
| company scope mismatch | `blocked`；mapping 不返回；建立 audit reference |
| machine 不在同一 company | `blocked`／`TIANLAI_INVALID_MACHINE` |
| commodity 不存在或 ID／code 衝突 | `blocked` 或 `manual_review` |
| 同一 machine＋layer 對到多個商品 | `manual_review`／`TIANLAI_MAPPING_CONFLICT` |
| timeout／未知 state | `unknown`；不自動重送 |
| response 缺必要欄位 | `blocked`／`BLOCKED_BY_ENDPOINT_SCHEMA` |
| empty list | `empty`；不偽造商品、mapping 或庫存 |

## 五、不得實作或宣稱

本交接不授權 `Coupon.aspx`、`VipOrder.aspx`、Sales、預訂、發券、開門、出貨、取消、庫存寫入、正式付款或退款。Focused run 已排除 Coupon、VipOrder 與 Sales；所有設備異常均為 generic synthetic。T2 不得把 `state=0`、HTTP 200 或 fixture PASS 當成正式 API、正式 mapping 或實機驗收。

## 六、解除阻塞所需回覆

| Owner 輸入 | 必要內容 |
|---|---|
| Dennis／天來 API owner | v2.7 第 10 節原檔、版本日期、正式 request sample 位置 |
| 天來 API owner | Base URL 環境分類、MachineCommodity method／fields／response、company scope |
| Credential owner | 受控測試 Token 注入、rotation 與 audit owner；秘密值不得進 Git／log |
| 設備 owner | 精確機型、layer／slot schema、測試機、地點、時段與 reset 方法 |

以上資料核准後，T7 才可依 Work Order 對 Machine、Commodity、MachineCommodity 各執行最多一個最小唯讀 query。未核准前，整體狀態維持 `BLOCKED_BY_ENDPOINT_SCHEMA`。

## References

[1]: ./tianlai_v27_readback.json "天來 v2.7 readback"
[2]: ./tianlai_v27_status_mapping.md "天來 v2.7 status mapping"
[3]: https://github.com/pingoapple88/stallpay-v2/blob/f883fa9e617b41e8e0885ad821975f56bb6ae99f/server/_core/vendingMachineProvider.ts "IVendingMachineProvider"
[4]: https://github.com/pingoapple88/stallpay-v2/blob/f883fa9e617b41e8e0885ad821975f56bb6ae99f/server/vending/providers/tenlife/tenlifeClient.ts "Tenlife client"
[5]: https://github.com/pingoapple88/stallpay-v2/blob/f883fa9e617b41e8e0885ad821975f56bb6ae99f/server/vending/providers/tenlifeVendingProvider.ts "Tenlife provider wrapper"
