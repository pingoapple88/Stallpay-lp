
## 第四開發批次：商業規則、設備連動與結算預覽

已建立校鮮集專屬的商品定價、會員點數／回饋金、利潤分配、資金流、發票責任與動態結算 contract。價格、比例、通路、稅務口徑、規則版本與結算責任均不寫死。

`/api/v1/mock/rewards/preview`、`/api/v1/mock/device-inventory/apply` 與 `/api/v1/mock/settlements/reconcile-preview` 只接受 `X-Demo-Mode: true`。它們用於 synthetic／Device Simulator 驗證，不會付款、開發票、申報、撥款、修改正式庫存或發送通知。

Device Simulator 僅允許同 organization、同 device、同 SKU 的 accepted event；補貨、預留與扣減可重播測試，scope 不符、庫存不足與非 accepted 狀態會拒絕或保持 blocked。

資金流、發票流與結算流在 owner 尚未確認責任主體時維持 `blocked`；因此目前不能自動完成財稅申報、發票開立、付款扣款或利潤分配。
