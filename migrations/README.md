# Migrations

本版本是純靜態企業展示原型，不建立 PostgreSQL schema，也不保存會員、訂單、付款或公司資料，因此沒有可執行的 migration。

正式導入時，資料層應由獨立的 Python FastAPI + SQLAlchemy + PostgreSQL 專案負責，並至少由核准 owner 定義：

- `company_id` 與校點租戶範圍
- 會員 PII 加密、遮罩與保留政策
- 商品、團購檔期、訂單、配送／取貨與對帳資料
- `audit_logs` 與事件發布紀錄
- LINE、Order AI、MerchLoop、StallPay 的 Adapter 設定

正式 schema、migration 與資料環境：`[TODO: 待人工確認]`。
