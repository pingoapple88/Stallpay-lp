#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
HTML = ROOT / "index.html"
CONFIG = ROOT / "config.js"
METADATA = ROOT / "build-metadata.js"
BUILD_SCRIPT = REPO / "scripts" / "build_t7_test_site.py"

html = HTML.read_text(encoding="utf-8")
config = CONFIG.read_text(encoding="utf-8")
metadata = METADATA.read_text(encoding="utf-8")
builder = BUILD_SCRIPT.read_text(encoding="utf-8")

required_markers = [
    "智販機 Synthetic 測試工作台",
    "T7-VENDOR-SYNTHETIC-03",
    "quickLoadBtn",
    "quickRunAllBtn",
    "quickViewResultsBtn",
    "quickExportBtn",
    "saveSetupBtn",
    "runSelectedBtn",
    "runAllBtn",
    "exportJsonBtn",
    "exportCsvBtn",
    "page_revision",
    "content_source_revision",
    "parent",
    "source_revision_semantics:'page_revision'",
    "evidence_commit",
    "metadata_binding_commit",
    "fixture_path",
    "operation_ref",
    "idempotency_key_ref",
    "audit_ref",
    "request_timestamp_utc",
    "response_timestamp_utc",
    "exit_code",
    "artifact_sha256",
    "formal_connections:false",
    "real_api_query_count:0",
    "formal_device_control:false",
    "formal_inventory_write:false",
    "test_device_verified:false",
    "gate_06:'BLOCKED'",
    "retryable:false",
    "NEEDS_RECONCILIATION",
    "MANUAL_REVIEW",
    "crypto?.subtle",
    'aria-live="polite"',
    'aria-live="assertive"',
    'role="alert"',
    'aria-describedby="longErrorDetail"',
    "longErrorText",
    "queryParams.get('fixture')==='long-error'",
    "runSuite(['malformed_json'])",
    ":focus-visible",
    "prefers-reduced-motion",
]
for marker in required_markers:
    assert marker in html, f"missing HTML marker: {marker}"

for quick_label in ["1. 載入 Synthetic", "2. 執行全部 Mock", "3. 查看結果", "4. 匯出報告"]:
    assert quick_label in html, f"missing primary quick flow label: {quick_label}"
assert 'class="advanced-panel"' in html

for identifier_id in ["batchName", "deviceId", "storeKey", "machineCode", "commodityCode", "slot", "sku"]:
    assert re.search(rf'<input\s+id="{identifier_id}"[^>]*\sreadonly\s*/?>', html), f"identifier must be readonly: {identifier_id}"
for marker in [
    "SYNTHETIC_PATTERNS",
    "setupIsSynthetic",
    "canonicalSetup",
    "SYNTHETIC_ALLOWLIST_BLOCKED",
    "EXPORT_BLOCKED_NON_SYNTHETIC_OR_UNSTAMPED",
    "setup:canonicalSetup",
    "machine_ref:'SYNTHETIC_MACHINE'",
    "runRuntimeSelfTest",
    "hostile_identifier_blocked",
]:
    assert marker in html, f"missing redaction marker: {marker}"
assert "setup:{...state.setup" not in html, "raw setup spread must not enter exports"

for forbidden_id in [
    "realPreflightBtn", "adapterHealthBtn", "testerAccessKey", "managerAccessKey",
    "managerToken", "loadCredentialStatusBtn", "saveCredentialBtn", "rollbackCredentialBtn",
]:
    assert f'id="{forbidden_id}"' not in html, f"forbidden DOM path remains: {forbidden_id}"

for forbidden_runtime in [
    r"\bfetch\s*\(", r"(?:new\s+)?XMLHttpRequest\s*\(", r"(?:new\s+)?WebSocket\s*\(",
    r"(?:navigator\.)?sendBeacon\s*\(", r"localStorage", r"sessionStorage", r"indexedDB",
    r"/api/v1/t7/network/preflight", r"/api/v1/t7/settings",
]:
    assert not re.search(forbidden_runtime, html, re.IGNORECASE), f"forbidden runtime path: {forbidden_runtime}"

assert not re.search(r"https?://", html, re.IGNORECASE), "HTML contains an external URL"
assert "adapterBaseUrl: ''" in config
assert "realPreflightEnabled: false" in config
assert "credentialManagement: 'DISABLED'" in config
assert "formalConnections: false" in config
assert "realApiQueryCount: 0" in config
assert "formalDeviceControl: false" in config
assert "formalInventoryWrite: false" in config
assert "testDeviceVerified: false" in config
assert "gate06: 'BLOCKED'" in config
assert not re.search(r"https?://", config, re.IGNORECASE), "config contains an external URL"

expected_locales = ["zh-Hant-TW", "en-US", "th-TH", "ja-JP", "id-ID"]
for locale in expected_locales:
    assert f'value="{locale}"' in html
    assert f"'{locale}':" in html

scenario_ids = re.findall(r"\['([a-z0-9_]+)','(?:PASS|ATTENTION|BLOCKED)'", html)
assert len(scenario_ids) == 24, f"scenario count must be 24, got {len(scenario_ids)}"
assert len(set(scenario_ids)) == 24, "scenario IDs must be unique"

for marker in [
    "T7-BUILD-METADATA-02",
    "page_revision: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "content_source_revision: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "parent: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "evidence_commit: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "metadata_binding_commit: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "stamped: false",
    "exit_code: 3",
    "rollback: '6ee1b866e4e07c35800521f67834f1be647c4bbd'",
    "real_api_query_count: 0",
    "formal_device_control: false",
    "formal_inventory_write: false",
    "test_device_verified: false",
    "gate_06: 'BLOCKED'",
]:
    assert marker in metadata, f"missing fail-closed source metadata: {marker}"

for marker in [
    'git("rev-parse", "HEAD")',
    'git("rev-parse", "HEAD^")',
    '"page_revision": head',
    '"content_source_revision": head',
    '"parent": parent',
    '"evidence_commit": head',
    '"metadata_binding_commit": head',
    '"stamped": True',
    '"exit_code": 0',
    "TRACKED_WORKTREE_MUST_BE_CLEAN_BEFORE_STAMPING",
]:
    assert marker in builder, f"missing artifact builder marker: {marker}"

for secret_pattern in [
    r"Bearer\s+[A-Za-z0-9._-]{12,}", r"AKIA[A-Z0-9]{16}", r"sk-[A-Za-z0-9]{16,}",
    r"-----BEGIN\s+.*PRIVATE\s+KEY-----",
]:
    assert not re.search(secret_pattern, html + config + metadata + builder), f"secret pattern found: {secret_pattern}"

print("static_site_validation=PASS")
print("schema_version=T7-VENDOR-SYNTHETIC-03")
print("scenario_count=24")
print("locales=zh-Hant-TW,en-US,th-TH,ja-JP,id-ID")
print("primary_quick_flow=load_synthetic,run_all_mock,view_results,export_report")
print("identifier_redaction=ALLOWLIST_AND_CANONICAL_REDACTION")
print("source_metadata=UNSTAMPED_FAIL_CLOSED_TEMPLATE")
print("build_artifact_provenance=GIT_HEAD_AND_PARENT")
print("long_error_fixture=malformed_json")
print("external_runtime_connections=NONE")
print("credential_dom_paths=NONE")
print("formal_connections=false")
print("real_api_query_count=0")
print("formal_device_control=false")
print("formal_inventory_write=false")
print("test_device_verified=false")
print("gate_06=BLOCKED")
