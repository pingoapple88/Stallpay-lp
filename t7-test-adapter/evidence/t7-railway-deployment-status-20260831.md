# T7 Railway Adapter deployment status — 2026-08-31

- Railway project: `https://railway.com/project/09fdbeb2-8d86-4b38-921a-87e10f363f7d`
- Service ID: `554449b3-73d8-44ac-ba7e-e608efda7b17`
- Environment ID: `2fdb218d-0576-41f7-a35a-5c504ebf6567`
- Public Adapter origin: `https://stallpay-lp-production.up.railway.app`
- Health endpoint: `https://stallpay-lp-production.up.railway.app/healthz`
- Production test console: `https://go.stall.merchcore.ai/t7-test`
- Runtime source repository: `pingoapple88/Stallpay-lp`, root directory `/t7-test-adapter`, branch `main`.
- PostgreSQL is provisioned in the same project; `DATABASE_URL` is supplied using Railway reference variable. No database password was copied or recorded.
- Pre-deploy command: `python scripts/run_migrations.py`.
- Initial crash 1: SQLAlchemy selected psycopg2 for `postgresql://`; fixed by normalizing to `postgresql+psycopg://` in commit `a47a4881adb7cc0802b69c618fc3e3c2cbd2a8ba`.
- Initial crash 2: migration command had not been configured, so tables were absent. Railway pre-deploy migration was then enabled.
- Safe health response after migration: `status=ok`, `database_configured=true`, `manager_access_configured=true`, `tester_access_configured=true`, `credentials_configured=false`, `mode=READ_ONLY_TEST_ADAPTER`, `formal_device_control=false`, `completion_signal=false`, `gate_06=BLOCKED`.
- Public config source commit: `e6ed21ffd22a6b095426665f8d517dceac7c59dd`; it contains only the Adapter HTTPS origin and no company, token, manager key or tester key.
- Company bootstrap is `2000162`; Tianlai token intentionally remains unset because the supplied PDF／Excel contain sample signs but no recoverable token.
- Next required step: Dennis enters the existing Tianlai token through the TLS SUPER_ADMIN form using the manager access key. Then the tester key can execute Machine／Commodity read-only preflight.
- `TEST_DEVICE_VERIFIED=false`; GATE-06 remains `BLOCKED／TEST_DEVICE_REQUIRED`.
