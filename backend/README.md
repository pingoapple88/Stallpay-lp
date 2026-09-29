
## 第三開發批次：組織 scope 與 RBAC

已建立校鮮集專屬的 `organization`、`cooperative`、`school`、`supplier` 與 `device` scope contract，以及最小權限角色：組織管理者、合作社管理者、學校窗口、供應商操作員、設備操作員、財務覆核者、訂單覆核者與唯讀稽核者。

授權預設 fail-closed，必須同時符合 `principal_id`、`organization_id`、`scope_type`、`scope_id`、active binding 與 permission。供應商 scope 不可直接操作 device scope；跨 organization 查詢一律拒絕。

正式登入、JWT／session、principal directory、owner 核准與 production binding 尚未接入；本批次只提供校鮮集專屬 application contract、migration 與 focused tests。
