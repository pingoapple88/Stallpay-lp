
## 第六開發批次：Device Simulator 遠端監控與自動補貨

新增 mock-safe Device Simulator API：

- `POST /api/v1/mock/device-monitoring/telemetry`
- `GET /api/v1/mock/device-monitoring/telemetry/{telemetry_id}`
- `POST /api/v1/mock/device-monitoring/alerts/{alert_id}/acknowledge`

遙測內容包含 organization、device、supplier、SKU、可用庫存、低庫存門檻、連線狀態、溫度、UTC 時間與冪等鍵。低庫存會建立 `low_stock` 告警，若有 supplier scope 則產生 `requested` 狀態的 mock 補貨單；離線與溫度異常會轉為告警，不能自動操作設備。

`frontend/device-monitor.html` 提供遙測上報與告警展示介面。所有操作都要求 `X-Demo-Mode: true`，不連接真實販賣機、不自動開門、不扣款、不開票、不撥款。
