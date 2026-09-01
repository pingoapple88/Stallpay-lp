# WO-T7-W2-P1 執行報告

| 回報欄位 | 結果 |
|---|---|
| status | `BLOCKED_BY_ENDPOINT_SCHEMA`；synthetic fault harness=`COMPLETE` |
| executing_owner | `[TODO: 待人工確認]` |
| execution_environment | `LOCAL_SYNTHETIC_ONLY` |
| base_url_classification | `[TODO: 待人工確認]` |
| endpoint_name | `Machine.aspx`、`Commodity.aspx`、`MachineCommodity.aspx` |
| documented_http_method | `[TODO: 待 v2.7 owner 確認]`；既有 client 候選為 GET |
| request_fields_without_secret_values | Machine=`company/sign`；Commodity=`company/commodityCode?/commodityID?/sign`；MachineCommodity=`code/company/sign` |
| response_fields | Machine=`state/message/machine[]`；Commodity=`state/message/commodity[]`；Mapping=`state/message/commodity[].layer/commodityID/commodityCode/shelflife?` |
| http_status | `NOT_EXECUTED_REAL_API` |
| state | `NOT_OBSERVED_IN_THIS_WORK_ORDER` |
| message_redacted | `true` |
| evidence_path | `docs/t7-w2-p1/evidence/` |
| exit_code | focused client tests=`0`；fixture validation=`0`；device fault harness=`0` |
| rollback | 文件交付 rollback=`7cb348ad5235c4fe0a393aa2074b3856ab55a0ed`；API query=`NOT_APPLICABLE_READ_ONLY` |
| open_todos | v2.7 第 10 節、executing/API owner、Base URL 分類、company scope、MachineCommodity schema、credential owner、test-device |
| next_action | owner 核准前不執行真實 API；核准後每端點最多一個最小唯讀 query |

## 一、Repository 與版本

| 欄位 | 值 |
|---|---|
| Repository | `pingoapple88/Stallpay-lp` |
| Feature branch | `feat/t7-network-preflight` |
| Feature source commit | `45d9829cffb50028365f64288930082a529bfc71` |
| Main commit | `e6c80e790748fcbe018bb4cb971d5e642c723b9c` |
| Parent／rollback | `7cb348ad5235c4fe0a393aa2074b3856ab55a0ed` |
| Baseline client revision | `pingoapple88/stallpay-v2@f883fa9e617b41e8e0885ad821975f56bb6ae99f` |
| Commit author | `pingoapple88 <pingoapple88@users.noreply.github.com>` |

## 二、完成內容

本輪沒有執行真實 API，因為目前材料不能證明為 Work Order 指定的 API v2.7 第 10 節：供應商 PDF 無 `v2.7`／第 10 節標記，共享問答則稱現有文件為 v2.5。依 fail-closed 規則，真實 discovery 維持 `BLOCKED_BY_ENDPOINT_SCHEMA`。

| 交付 | 結果 |
|---|---|
| 文件核對／Request contract | 已完成；所有未核准 method／schema／scope 標 `[TODO: 待人工確認]` |
| Machine fixture | 9 synthetic cases |
| Commodity fixture | 9 synthetic cases |
| MachineCommodity fixture | 11 synthetic cases |
| Mapping fault coverage | 共 29 cases：success、empty、HTTP／API error、timeout、malformed、缺欄位、invalid machine／commodity、mapping conflict、scope mismatch |
| Focused client harness | 8 PASS、11 skipped、exit 0；只執行 Machine／Commodity／MachineCommodity／error handling |
| Device fault harness | 10 scenarios、failures=`[]`、exit 0 |
| T2 readback | 已完成 machine-readable JSON 與 handoff 文件 |
| 共享同步 | 看板、Manifest、evidence index、`T7_W2_P1_tianlai_v27/` 已更新 |

## 三、Changed paths

```text
docs/t7-w2-p1/T2_HANDOFF_tianlai_v27_readonly_mapping.md
docs/t7-w2-p1/evidence/tianlai_v27_device_fault_harness.log
docs/t7-w2-p1/evidence/tianlai_v27_device_fault_scenarios.json
docs/t7-w2-p1/evidence/tianlai_v27_fault_harness.log
docs/t7-w2-p1/evidence/tianlai_v27_mapping_fixture_validation.log
docs/t7-w2-p1/fixtures/commodity_mapping_fixture.json
docs/t7-w2-p1/fixtures/machine_commodity_mapping_fixture.json
docs/t7-w2-p1/fixtures/machine_mapping_fixture.json
docs/t7-w2-p1/source_inventory.md
docs/t7-w2-p1/tianlai_v27_document_and_request_contract.md
docs/t7-w2-p1/tianlai_v27_readback.json
docs/t7-w2-p1/tianlai_v27_status_mapping.md
```

本輪僅新增文件、synthetic fixture 與 log，沒有修改後端、登入、支付、資料庫 schema、migration、正式設備控制或 StallPay core。

## 四、驗證結果

| 驗證 | 結果 | Evidence |
|---|---|---|
| 三端點 focused mock tests | 8 passed／11 skipped／exit 0 | `evidence/tianlai_v27_fault_harness.log` |
| Mapping fixture validation | JSON／coverage／redaction／hash PASS；exit 0 | `evidence/tianlai_v27_mapping_fixture_validation.log` |
| Generic device fault harness | 10 scenarios／0 failures／exit 0 | `evidence/tianlai_v27_device_fault_harness.log` |
| Evidence artifact | 狀態序列、source revision、UTC、rollback 與安全旗標已保存 | `evidence/tianlai_v27_device_fault_scenarios.json` |
| Secret／real-data scan | PASS | Pre-commit QA |
| Legal-language scan | PASS | Pre-commit QA |
| Shadow／supplier-binary scan | PASS | Pre-commit QA |
| Git diff check | PASS | `git show --check e6c80e7...` |

## 五、邊界與風險

| 項目 | 判定 |
|---|---|
| 正式 v2.7 文件 | 未取得；`BLOCKED_BY_ENDPOINT_SCHEMA` |
| 真實 API query | 0 |
| 正式 Mapping | 未驗證 |
| Credential | `credentials_configured=false` |
| Coupon／VipOrder／Sales | Focused run 明確排除 |
| 寫入端點／開門／出貨 | 未執行 |
| 正式庫存／退款 | 未執行；T7 只輸出 intent |
| unknown／timeout | 不自動重送；需要 reconciliation／manual review |
| GATE-06 | `BLOCKED／TEST_DEVICE_REQUIRED` |
| `TEST_DEVICE_VERIFIED` | `false` |

## 六、T2 交接要求

T2 只能消費 synthetic fixture 的欄位與 canonical status；不能把 fixture 值、HTTP 200、`state=0` 或 harness PASS 當成供應商核准資料。Company scope 必須由 server context 決定；machine、commodity 或 layer 任一不一致時 fail-closed。金額由候選原生整數「元」轉 integer minor units，時間來源沒有時區時維持 TODO，不自行猜測。

## 七、交付檢查

| 檢查 | 結果 |
|---|---|
| 產出是否推送到 `pingoapple88` GitHub | 是；`main=e6c80e790748fcbe018bb4cb971d5e642c723b9c` |
| 是否新增外部 CDN、analytics、beacon 或 callback | 否 |
| Commit 作者是否為指定 Git 身份 | 是；`pingoapple88` |
| 是否含平台專屬執行期依賴或產出痕跡 | 否 |
| 最不確定部分 | v2.7 第 10 節、Base URL 分類、MachineCommodity schema 與 owner 均未取得核准 |
