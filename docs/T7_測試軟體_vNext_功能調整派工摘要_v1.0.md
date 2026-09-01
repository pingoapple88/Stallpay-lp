# StallPay T7 測試軟體 vNext 功能調整派工摘要

| 欄位 | 內容 |
|---|---|
| 文件版本 | v1.0 |
| 目標網址 | `https://go.stall.merchcore.ai/t7-test` |
| 本次模式 | `DEMO_MOCK`；保留既有 `READ_ONLY_TEST_ADAPTER` |
| 情境目標 | 32 個 P0 canonical 情境：12 個沿用補強＋20 個新增 |
| 正式設備控制 | 不納入；`formal_device_control=false` |
| 正式庫存／退款 | 不納入；只輸出 reconciliation／compensation intent |
| 完成訊號 | `completion_signal=false`；`GATE-06=BLOCKED` |
| 實作 owner | `[TODO: 待人工確認]` |

## 一、調整目標

目前測試頁已可讓現場人員執行十二種 synthetic 情境並匯出去敏證據，但與《StallPay 智販機整合完整情境清單》的 P0 要求相比，仍缺少多格履約、operation idempotency、scope mismatch、送出前後斷線、付款成功後例外、重複回執、錯格／錯品及 expected／actual 對照。

vNext 的目的，是把既有 browser 情境、generic fake-device 與安全規則整理成一套可追溯測試目錄。它不是天來控制程式，也不能取代 owner 核准的 API contract 或 test-device 驗證。

## 二、畫面調整

| 區塊 | 必須調整 | 驗收結果 |
|---|---|---|
| 情境篩選 | 增加 QR／scope、mapping／庫存、設備 operation、故障安全、對帳／補償五類 | 可按類別篩選、全選與清除 |
| 情境卡片 | 顯示 scenario ID、附件 source IDs、owner、mode、Gate、預期結果 | 使用者可在執行前看懂責任與限制 |
| 測試設定 | 增加 order ref、operation ref、idempotency key、payment state、machine／slot／commodity scope、多格清單 | 缺必要欄位時顯示 blocked，不產生假成功 |
| 執行結果 | 同時顯示 expected sequence、actual simulated sequence、差異與 safety assertions | 不一致時為 `NEEDS_REVIEW` |
| 多格結果 | 每格獨立顯示 slot、狀態與 receipt；再計算整單狀態 | 部分成功不可標 completed |
| 異常處理 | 顯示 retry allowed、reconciliation required、manual review、compensation intent | unknown 一律禁止自動重送 |
| 統計 | 顯示總數、PASS、ATTENTION、BLOCKED、MANUAL_REVIEW、NEEDS_RECONCILIATION | 統計與結果列一致 |
| 匯出 | JSON／CSV 增加 source IDs、expected／actual、owner、Gate、operation／audit ref、safety assertions | 不含 company 明文、Token、sign、PII 或 raw response |
| 完成判定 | 顯示 Simulator、Read-only Connectivity、Test-device 三層 | 只有實機證據與 Dennis 簽核才能申請第三層 |

## 三、情境批次

| 批次 | 內容 | 數量 | 執行條件 |
|---|---|---:|---|
| `P0-CORE-12` | 現有 QR、門鎖、鎖貨、unknown、售罄、離線、溫度、卡貨、固定資訊 | 12 | 沿用並補 source IDs／expected／actual |
| `P0-FAULT-07` | 送出前斷線、送出後斷線、timeout、busy、sensor conflict、malformed response、duplicate success | 7 | 全部 `DEMO_MOCK` |
| `P0-MULTISLOT-04` | 多格全成功、多格部分成功、錯格、錯品 | 4 | 每格獨立 receipt |
| `P0-SCOPE-IDEMPOTENCY-05` | company mismatch、wrong machine、mapping missing、same replay、payload conflict | 5 | mismatch／conflict fail-closed |
| `P0-PAID-EXCEPTION-03` | 已付款無空格、明確未出貨、結果 unknown | 3 | 不直接退款；只輸出 intent |
| `P0-OVER-DISPENSE-01` | 多出一件 | 1 | 記錄 discrepancy 與人工處理 |
| **合計** |  | **32** | 不執行正式設備控制 |

完整 scenario ID、附件對照與預期結果以 `T7_測試軟體_vNext_P0情境追蹤表.csv` 為準。

## 四、驗收條件

| 驗收編號 | 必須符合 |
|---|---|
| AC-01 | 32 個情境均可單獨執行，且 full suite 一次產生 32 筆結果。 |
| AC-02 | 每筆結果有唯一 test run ID、scenario ID、附件 source IDs、UTC、mode、owner 與 Gate。 |
| AC-03 | expected 與 actual sequence 可見；不一致自動標為 `NEEDS_REVIEW`。 |
| AC-04 | 同 operation 同 payload 重播不產生第二筆設備動作；同 key 不同 payload 為 `BLOCKED`。 |
| AC-05 | 送出後斷線、timeout、取貨 unknown 與付款結果 unknown 均為 `NEEDS_RECONCILIATION`，不得自動重送。 |
| AC-06 | 多格部分成功維持 `PARTIAL_FULFILLMENT`；每格 receipt 可追溯。 |
| AC-07 | company／store／machine／slot／commodity 任一 scope 不一致時 fail-closed。 |
| AC-08 | 卡貨、錯格、錯品、多出／少出、sensor conflict 只進 manual review／compensation intent。 |
| AC-09 | JSON／CSV 內容不含 secret、sign、PII、正式設備資料或 raw upstream body。 |
| AC-10 | `formal_device_control=false`、`formal_inventory_write=false`、`direct_refund=false`、`unknown_auto_resend=false`、`completion_signal=false`、`gate_06=BLOCKED`。 |
| AC-11 | 五語 fallback、桌機 1440×900、手機 390×844、Kiosk／平板、keyboard、focus、ARIA live 均有證據。 |
| AC-12 | focused test、compile、diff check、secret／external／shadow scan 均 exit 0，並提供 source commit、parent、rollback 與 evidence paths。 |

## 五、明確不做

| 不做項目 | 原因 |
|---|---|
| 不新增正式 `open_slot`／`dispense` endpoint | API v2.7、owner、Base URL、控制 contract 與 test-device 尚未核准 |
| 不將 Machine／Commodity HTTP 200 視為實機完成 | 唯讀連通不等於設備操作或出貨事實 |
| 不執行正式支付／退款／發票 | 屬對應 owner 與中央 Gate |
| 不修改 ERP 正式庫存 | ERP Core 是唯一正式 inventory truth |
| 不猜測天來 fault code、slot schema、sensor 或 webhook | 未知內容維持 `[TODO: 待人工確認]` |
| 不以 Mock 截圖解除 GATE-06 | 必須有指定 test-device、真實 receipt、對帳與 Dennis 簽核 |

## 六、交付物

| 交付物 | 必要內容 |
|---|---|
| 更新後測試頁 | 32 情境、分類、設定、expected／actual、多格、統計、匯出 |
| Canonical fixture | 32 情境的固定輸入、狀態序列、結果與安全斷言 |
| Focused validator | 檢查 scenario count、ID 唯一、狀態、redaction、Gate 與 safety assertions |
| Browser evidence | 桌機、手機與完整套件結果；不含 credential |
| Machine-readable snapshot | source revision、UTC、scenario counts、exit codes、Gate、rollback |
| 文件更新 | Quick Start、操作手冊、共享看板、Manifest、evidence index |
