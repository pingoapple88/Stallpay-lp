#!/usr/bin/env sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
cd "$REPO_ROOT"

LOG="t7-test/evidence/t7-prepublish-smoke-20260831.log"
mkdir -p "$(dirname "$LOG")"
: > "$LOG"

run_checks() {
  date -u '+utc=%Y-%m-%dT%H:%M:%SZ'
  printf 'base_sha=%s\n' "$(git rev-parse HEAD)"

  python3 t7-test/tests/validate_static_site.py
  python3 -m compileall -q t7-test/tests
  printf 'compile_exit=0\n'

  git diff --check
  printf 'diff_check_exit=0\n'

  T7_STATUS=$(curl -sS --max-time 5 -o /tmp/t7-index.html -w '%{http_code}' http://127.0.0.1:4180/t7-test/)
  test "$T7_STATUS" = "200"
  grep -Fq '天來無人銷售測試模式' /tmp/t7-index.html
  printf 't7_path_http_smoke=0\n'

  ROOT_STATUS=$(curl -sS --max-time 5 -o /tmp/stallpay-root.html -w '%{http_code}' http://127.0.0.1:4180/)
  test "$ROOT_STATUS" = "200"
  grep -Fq 'StallPay' /tmp/stallpay-root.html
  printf 'root_homepage_smoke=0\n'

  if grep -ERin --exclude='t7-prepublish-smoke-20260831.log' -E 'Bearer[[:space:]]+[A-Za-z0-9._-]{12,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9]{16,}|-----BEGIN[[:space:]].*PRIVATE[[:space:]]KEY-----' t7-test; then
    printf 'secret_scan_exit=1\n'
    return 1
  fi
  printf 'secret_scan_exit=0\n'

  if grep -Ein 'fetch\(|XMLHttpRequest|WebSocket|sendBeacon|localStorage|sessionStorage|indexedDB|https?://[^[:space:]]+\.(js|css)' t7-test/index.html; then
    printf 'runtime_external_scan_exit=1\n'
    return 1
  fi
  printf 'runtime_external_scan_exit=0\n'
}

run_checks 2>&1 | tee "$LOG"
sha256sum t7-test/index.html "$LOG"
