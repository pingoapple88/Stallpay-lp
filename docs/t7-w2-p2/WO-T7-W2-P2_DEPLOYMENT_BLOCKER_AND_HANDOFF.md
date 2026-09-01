# WO-T7-W2-P2｜部署阻塞與修正交接

| 欄位 | 判定 |
|---|---|
| `status` | `BLOCKED_BY_MISSING_SOURCE_ARTIFACT` |
| `repository` | `pingoapple88/Stallpay-lp` |
| `required_branch` | `feat/t7-simple-test-flow` |
| `required_source_commit` | `6ee1b866e4e07c35800521f67834f1be647c4bbd` |
| `required_parent／rollback` | `32561cd9c0c9c5d3fdf3edff3ba58a813f7d18c6` |
| `required_changed_paths` | `t7-test/index.html`、`scripts/validate_t7_simple_flow.py` |
| `public_site` | `https://go.stall.merchcore.ai/t7-test/` |
| `deployment_performed` | `false` |
| `real_api_query_count` | `0` |
| `formal_device_control` | `false` |
| `formal_inventory_write` | `false` |
| `GATE-06` | `BLOCKED` |

> **部署判定：**附件報告聲稱 quick flow 已在本機 commit `6ee1b866...` 完成，但目前核准 repository 的本機 object database、GitHub commit API、remote branch 與使用者 GitHub code search 均找不到該 commit／branch；附件也未包含 patch、Git bundle 或兩個 changed paths 的完整來源。因此不能把報告文字當成可部署原始碼。[1]

## 一、已執行的來源查找

| 查找位置 | 結果 |
|---|---|
| `/home/ubuntu/Stallpay-lp-deploy` local object | `6ee1b866...` 不存在 |
| `origin/feat/t7-simple-test-flow` | remote ref 不存在 |
| GitHub commit API | `No commit found for SHA` |
| 使用者 GitHub code search：`quickRunBtn` | 0 筆 |
| `/home/ubuntu/work/stallpay-t7-site` | 目錄不存在 |
| `/home/ubuntu` 全文搜尋 | 只有附件報告／evidence 提及 `quickRunBtn`，沒有 HTML／JS 實作 |
| 本次附件 | 沒有 `.patch`、`.bundle`、quick-flow `index.html` 或 `validate_t7_simple_flow.py` |

## 二、為何不能部署現行 main

現行 main 的舊頁面雖能通過既有 12 情境 validator，但該 validator 的驗收標準仍要求 `realPreflightBtn`、`managerAccessKey`、`saveCredentialBtn` 與 `rollbackCredentialBtn` 存在，與 P2 hardening 要求相反。[2] 現行頁面仍公開顯示真實唯讀 preflight CTA 與完整 SUPER_ADMIN credential save／rollback controls，且按鈕未 disabled。[3]

| P2 驗收項目 | 現行 main | 結果 |
|---|---:|---|
| `quickRunBtn`／四步 quick flow | 0 | `FAIL` |
| 每筆 `source_revision` | 0 | `FAIL` |
| 每筆 `evidence_commit` | 0 | `FAIL` |
| 每筆 `fixture_path` | 0 | `FAIL` |
| 每筆 `operation_ref` | 0 | `FAIL` |
| 每筆 `idempotency_key_ref` | 0 | `FAIL` |
| 每筆 `audit_ref` | 0 | `FAIL` |
| `real_api_query_count=0` 顯示／匯出 | 0 | `FAIL` |
| `scope_mismatch` | 0 | `FAIL` |
| `mapping_conflict` | 0 | `FAIL` |
| `payload_mismatch` | 0 | `FAIL` |
| `saveCredentialBtn`／`rollbackCredentialBtn` | 各 2 個 marker | `FAIL_GENERAL_TESTER_ISOLATION` |
| `realPreflightBtn` disabled | 0 | `FAIL` |
| 現行 self-service scenarios | 12 | `FAIL_MINIMUM_18` |
| 舊版 safety | `formal_device_control=false`、`formal_inventory_write=false`、`GATE-06=BLOCKED` | `PASS_BASELINE_ONLY` |

完整 raw audit：`evidence/t7_p2_baseline_audit_20260901.log`，SHA-256=`61eddf5867ad55de3c7be5eead791fc53ca1b702ec2870099e1554a7d78211e9`。

## 三、不得採取的替代方案

不得把現行 main 重新部署後宣稱 quick flow 已完成；不得依附件報告重新手工猜測原 commit；不得僅以 CSS 隱藏 credential controls 而保留可觸發 handler；不得讓一般測試頁產生任何天來 request；不得把 adapter health、HTTP 200、12 個舊 Mock 或本機報告當成公開 P2 hardening 證據。

## 四、需要補回的最小 source artifact

| 選項 | 必須提供的內容 | 可驗證條件 |
|---|---|---|
| Git branch | 推送 `feat/t7-simple-test-flow` 至 `pingoapple88/Stallpay-lp` | branch HEAD 必須為 `6ee1b866...` 或提供新的 40 字元 commit 與 parent |
| Patch | `git format-patch -1 6ee1b866...` 產出的 `.patch` | patch 必須只修改原報告所列兩個 paths，author 為 `pingoapple88` |
| Git bundle | 包含 branch／commit 的 `.bundle` | `git bundle verify` 通過，可讀 parent 與 changed paths |
| 完整來源檔 | quick-flow 版 `t7-test/index.html` 與 `scripts/validate_t7_simple_flow.py` | 另附 SHA-256 與 source／parent；不得只有瀏覽器另存的舊公開頁 |

## 五、取得來源後的核准實作檢核

即使找回 `6ee1b866...`，附件報告也已明載該 commit 尚未完成 P2 hardening。核准實作者必須在同一 branch 追加修正並滿足以下條件；T7 驗證端才可部署。

| 類別 | 必須完成 |
|---|---|
| Quick flow | 首頁收斂為「載入 Synthetic → 執行全部 Mock → 查看結果 → 匯出報告」，快速與進階執行共用單一 output schema |
| 高風險 CTA | 真實 preflight disabled；每個控制顯示 `DEMO_MOCK`、`formal_device_control=false`、`formal_inventory_write=false`、`real_api_query_count=0` |
| Credential RBAC UI | 一般測試人員 DOM／keyboard／event path 不能看到或觸發 save／rollback；不得只靠折疊或 CSS 隱藏 |
| Fault screens | 至少 18 情境；新增 malformed response、API state error、scope mismatch、mapping conflict、duplicate idempotency、payload mismatch、manual review |
| Unknown | 顯示 `unknown`／`NEEDS_RECONCILIATION`／`MANUAL_REVIEW`；`retryable=false`，不得自動重送 |
| Export | 每筆含 `source_revision`、`evidence_commit`、`fixture_path`、`operation_ref`、`idempotency_key_ref`、`audit_ref`、UTC、exit code 與 SHA-256 |
| Export redaction | 不含 Token、sign、完整 URL、password、PII、正式 company／machine／commodity 識別；CSV 僅供人讀 |
| i18n | `zh-Hant-TW`、`en-US`、`th-TH`、`ja-JP`、`id-ID` 核心四步可完成；缺字串 fallback 至繁中 |
| Accessibility | 1440×900、390×844、keyboard-only、focus-visible、ARIA live、reduced motion、長錯誤訊息均有 evidence |
| Gate | `real_api_query_count=0`、`completion_signal=false`、`GATE-06=BLOCKED`、`TEST_DEVICE_VERIFIED=false` |

## 六、部署前後命令與證據要求

| 階段 | 要求 |
|---|---|
| Focused test | 新 validator 必須檢查 quick IDs、18+ scenarios、metadata、credential DOM isolation、preflight disabled、redaction 與五語系 |
| Compile／syntax | HTML inline JavaScript syntax check exit 0 |
| Diff | `git diff --check parent..HEAD` exit 0 |
| Scan | external／secret／shadow／credential／production identifier scan exit 0 |
| Browser | 本機與公開 URL 均執行四步 quick flow；JSON 重新讀取並重算 artifact SHA-256 |
| RWD／a11y | 桌機、手機、keyboard、focus-visible、ARIA live evidence 各自保存 |
| Deployment | 只部署通過以上檢查的 `main` revision；Cloudflare propagation 後核對公開 config 與 HTML |

## 七、目前 next action

請提供上述四種 source artifact 之一。收到後，先驗證 source SHA／parent／changed paths，再檢查 P2 hardening；若符合則同步 main 觸發既有 Cloudflare Pages 發布，最後執行公開四步 smoke。正式 v2.7 第 10 節與 owner 未取得前，真實 API 與設備控制持續封鎖。

## References

[1]: ./source_inventory.md "WO-T7-W2-P2 去敏來源清冊"
[2]: https://github.com/pingoapple88/Stallpay-lp/blob/32561cd9c0c9c5d3fdf3edff3ba58a813f7d18c6/t7-test/tests/validate_static_site.py "現行靜態 validator"
[3]: https://github.com/pingoapple88/Stallpay-lp/blob/32561cd9c0c9c5d3fdf3edff3ba58a813f7d18c6/t7-test/index.html "現行 T7 測試頁來源"
