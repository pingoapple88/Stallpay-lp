# 校鮮集正式後端開發基線

本目錄是校鮮集獨立的 Python FastAPI + SQLAlchemy／PostgreSQL 正式產品開發起點，與根目錄的展示網站分離。

## 目前已建立

- `/healthz` 服務健康檢查。
- `/api/v1/governance/status` 治理與外部整合狀態檢查。
- provider-neutral Adapter contracts：LLM、ERP、庫存、發票、付款、設備、通知。
- `organizations` scope 與 append-only `audit_logs` 初始 migration。
- Dockerfile、docker-compose、`.env.example`。

## 目前明確未連接

正式 ERP、付款、發票、LINE、設備與 LLM endpoint 都尚未接入。`FORMAL_SERVICE_CONNECTED=false` 時，外部整合維持 blocked，不能建立正式交易、申報、扣款或設備控制。

## 啟動

```bash
cp .env.example .env
# 修改 .env 中的密碼與 JWT_SECRET；不要提交 .env
docker compose up --build
curl http://localhost:8000/healthz
curl http://localhost:8000/api/v1/governance/status
```

## 下一個正式開發批次

1. owner 核准 organization／company／store scope 與 RBAC 角色。
2. 建立校鮮集專屬 authentication、RBAC、PII 與 audit service。
3. 建立商品／SKU、團購檔期、訂單與庫存的校鮮集 contract。
4. 建立供應商自行補貨與智販機設備規則的版本化模型。
5. 以 synthetic fixture 建立 OrderAI 人工覆核與 ERP blocked／mock 流程。
6. owner 核准後才新增 provider implementations 與正式連線設定。

## 專案邊界

請先閱讀根目錄的 [`PROJECT_BOUNDARY.md`](../PROJECT_BOUNDARY.md)。不得從萬佳鄉、雲鼎 ERP、捷州 ERP、StallPay 核心專案或其他 repository 直接帶入客戶資料、正式 endpoint、credential、商品／價格、稅務規則、migration 或 production mapping。
