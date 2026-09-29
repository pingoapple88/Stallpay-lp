
## 第五開發批次：供應商自助補貨與結算管理後台

新增 mock-safe 管理 API：

- `POST /api/v1/mock/operations/restock/requests`
- `POST /api/v1/mock/operations/restock/requests/{request_id}/review`
- `POST /api/v1/mock/operations/settlements`
- `GET /api/v1/mock/operations/settlements/{batch_id}/report`
- `POST /api/v1/mock/operations/settlements/{batch_id}/review`

所有 endpoint 都要求 `X-Demo-Mode: true`。補貨申請建立後維持 `requested`，只有人工核准才會進入 `authorized`；拒絕與要求補件不會修改庫存。

`frontend/restock-settlement-admin.html` 是供應商自助補貨與財務人工覆核的純 HTML／JavaScript 操作介面，透過 fetch 串接上述 mock API。正式登入、RBAC middleware、SQLAlchemy repository 與外部 ERP／付款／發票連線仍待 owner 核准及下一階段實作。
