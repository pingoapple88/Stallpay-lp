# Migration status

本 T7 自助測試頁為 browser-only static asset，不使用 database，不建立 schema，不修改正式庫存，也不產生 migration。

若後續新增集中式測試結果保存，必須另行建立經 data owner 核准的 PostgreSQL migration、company scope、RBAC、audit log、PII 保護與 rollback，並在 GATE-04／GATE-06 通過後才能部署。
