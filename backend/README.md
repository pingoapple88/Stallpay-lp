
## 已新增的第二開發批次

- `app/domain_rules.py`：版本化金額、比例、稅務口徑、結算週期與有效期間 contract。
- `app/restock.py`：供應商自行補貨申請、授權、驗收與對帳狀態 contract。
- `migrations/0002_dynamic_rules_supplier_restock.sql`：動態規則與補貨申請表。
- 未命中規則、未核准補貨或盤點差異不會自動扣庫、撥款或完成結算。

供應商自行補貨目前只建立「申請／授權／驗收」流程，不代表供應商已取得正式庫存 authority；正式權限、設備範圍、補貨 SLA、商品 owner 與結算規則仍須校鮮集 owner 核准。
