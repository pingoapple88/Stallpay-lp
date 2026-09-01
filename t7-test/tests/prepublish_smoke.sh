#!/usr/bin/env sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)
cd "$REPO_ROOT"

LOG="t7-test/evidence/t7-p2-hardening-prepublish.log"
mkdir -p "$(dirname "$LOG")"
: > "$LOG"

run_checks() {
  date -u '+utc=%Y-%m-%dT%H:%M:%SZ'
  printf 'source_commit=%s\n' "$(git rev-parse HEAD)"
  printf 'branch=%s\n' "$(git branch --show-current)"
  printf 'parent=%s\n' "$(git rev-parse HEAD^)"
  printf 'rollback=6ee1b866e4e07c35800521f67834f1be647c4bbd\n'

  python3 scripts/validate_t7_simple_flow.py
  printf 'quick_flow_validator_exit=0\n'
  python3 t7-test/tests/validate_static_site.py
  printf 'static_site_validator_exit=0\n'
  python3 -m compileall -q scripts t7-test/tests
  python3 -m py_compile scripts/build_t7_test_site.py
  printf 'compile_exit=0\n'
  printf 'artifact_builder_compile_exit=0\n'

  node --check t7-test/build-metadata.js
  printf 'metadata_syntax_exit=0\n'
  node --check t7-test/config.js
  printf 'config_syntax_exit=0\n'
  sed -n '/<script>$/,/<\/script>/p' t7-test/index.html | sed '1d;$d' > /tmp/t7-p2-inline.js
  node --check /tmp/t7-p2-inline.js
  rm -f /tmp/t7-p2-inline.js
  printf 'inline_javascript_syntax_exit=0\n'

  git diff --check
  printf 'diff_check_exit=0\n'

  T7_STATUS=$(curl -sS --max-time 5 -o /tmp/t7-p2-index.html -w '%{http_code}' http://127.0.0.1:4180/t7-test/)
  test "$T7_STATUS" = "200"
  grep -Fq '智販機 Synthetic 測試工作台' /tmp/t7-p2-index.html
  rm -f /tmp/t7-p2-index.html
  printf 't7_path_http_smoke=0\n'

  if grep -ERin --exclude='t7-p2-hardening-prepublish.log' -E 'Bearer[[:space:]]+[A-Za-z0-9._-]{12,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9]{16,}|-----BEGIN[[:space:]].*PRIVATE[[:space:]]KEY-----' t7-test scripts; then
    printf 'secret_scan_exit=1\n'
    return 1
  fi
  printf 'secret_scan_exit=0\n'

  if grep -Ein 'fetch\(|XMLHttpRequest[[:space:]]*\(|WebSocket[[:space:]]*\(|sendBeacon[[:space:]]*\(|localStorage\.|sessionStorage\.|indexedDB[[:space:]]*\(|https?://' t7-test/index.html t7-test/config.js; then
    printf 'runtime_external_scan_exit=1\n'
    return 1
  fi
  printf 'runtime_external_scan_exit=0\n'

  if grep -Ein 'realPreflightBtn|adapterHealthBtn|testerAccessKey|managerAccessKey|managerToken|saveCredentialBtn|rollbackCredentialBtn|/api/v1/t7/network/preflight|/api/v1/t7/settings' t7-test/index.html; then
    printf 'high_risk_path_scan_exit=1\n'
    return 1
  fi
  printf 'high_risk_path_scan_exit=0\n'
}

run_checks 2>&1 | tee "$LOG"
sha256sum t7-test/index.html t7-test/config.js t7-test/build-metadata.js scripts/build_t7_test_site.py scripts/validate_t7_simple_flow.py t7-test/tests/validate_static_site.py "$LOG"
