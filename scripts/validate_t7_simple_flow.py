#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "t7-test" / "index.html"
METADATA = ROOT / "t7-test" / "build-metadata.js"
BUILD_SCRIPT = ROOT / "scripts" / "build_t7_test_site.py"

html = HTML.read_text(encoding="utf-8")
metadata = METADATA.read_text(encoding="utf-8")
build_script = BUILD_SCRIPT.read_text(encoding="utf-8")

required_ids = {
    "locale",
    "quickLoadBtn",
    "quickRunAllBtn",
    "quickViewResultsBtn",
    "quickExportBtn",
    "saveSetupBtn",
    "selectAllBtn",
    "runSelectedBtn",
    "runAllBtn",
    "exportJsonBtn",
    "exportCsvBtn",
    "clearBtn",
    "scenarioGrid",
    "resultRows",
    "longErrorDetail",
    "setupStatus",
    "runStatus",
}
missing_ids = sorted(element_id for element_id in required_ids if f'id="{element_id}"' not in html)
assert not missing_ids, f"missing required element IDs: {missing_ids}"

forbidden_ids = {
    "realPreflightBtn",
    "adapterHealthBtn",
    "testerAccessKey",
    "managerAccessKey",
    "managerToken",
    "loadCredentialStatusBtn",
    "saveCredentialBtn",
    "rollbackCredentialBtn",
}
present_forbidden_ids = sorted(element_id for element_id in forbidden_ids if f'id="{element_id}"' in html)
assert not present_forbidden_ids, f"forbidden high-risk DOM IDs remain: {present_forbidden_ids}"

forbidden_runtime_patterns = {
    "fetch": r"\bfetch\s*\(",
    "xhr": r"(?:new\s+)?XMLHttpRequest\s*\(",
    "websocket": r"(?:new\s+)?WebSocket\s*\(",
    "beacon": r"(?:navigator\.)?sendBeacon\s*\(",
    "local_storage": r"localStorage",
    "session_storage": r"sessionStorage",
    "indexed_db": r"indexedDB",
    "adapter_url": r"adapterBaseUrl",
    "credential_route": r"/api/v1/t7/settings",
    "preflight_route": r"/api/v1/t7/network/preflight",
}
for name, pattern in forbidden_runtime_patterns.items():
    assert not re.search(pattern, html, re.IGNORECASE), f"forbidden runtime path remains: {name}"

script_sources = re.findall(r'<script\s+src="([^"]+)"', html)
assert script_sources == ["./build-metadata.js"], f"unexpected script sources: {script_sources}"
assert not re.search(r"https?://", html + metadata, re.IGNORECASE), "source must not contain external URLs"

locale_values = re.findall(r'<option\s+value="([^"]+)">', html)
expected_locales = ["zh-Hant-TW", "en-US", "th-TH", "ja-JP", "id-ID"]
assert locale_values[:5] == expected_locales, f"locale set/order mismatch: {locale_values[:5]}"
for locale in expected_locales:
    assert f"'{locale}':" in html, f"missing translation dictionary: {locale}"

scenario_ids = re.findall(r"\['([a-z0-9_]+)','(?:PASS|ATTENTION|BLOCKED)'", html)
expected_scenarios = {
    "happy_path", "fixed_info_report", "idempotency_replay", "duplicate_callback",
    "qr_invalid", "qr_expired", "door_blocked", "door_unknown",
    "goods_lock_conflict", "pickup_unknown", "inventory_empty", "network_offline",
    "temperature_attention", "lane_jam", "http_timeout", "http_non_2xx",
    "api_state_error", "malformed_json", "company_scope_mismatch", "machine_not_found",
    "commodity_not_found", "mapping_conflict", "payload_mismatch", "partial_dispense",
}
assert len(scenario_ids) == 24, f"scenario count must be 24, got {len(scenario_ids)}"
assert set(scenario_ids) == expected_scenarios, "scenario IDs do not match the approved P2 set"

required_contract_markers = [
    "T7-VENDOR-SYNTHETIC-03",
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
    "NEEDS_RECONCILIATION",
    "MANUAL_REVIEW",
    "retryable:false",
    "formal_connections:false",
    "real_api_query_count:0",
    "formal_device_control:false",
    "formal_inventory_write:false",
    "test_device_verified:false",
    "gate_06:'BLOCKED'",
    "crypto?.subtle",
    "SHA-256",
]
missing_markers = [marker for marker in required_contract_markers if marker not in html]
assert not missing_markers, f"missing contract markers: {missing_markers}"

required_quick_flow = [
    "1. 載入 Synthetic",
    "2. 執行全部 Mock",
    "3. 查看結果",
    "4. 匯出報告",
    'class="advanced-panel"',
    "loadSyntheticSetup",
]
missing_quick_flow = [marker for marker in required_quick_flow if marker not in html]
assert not missing_quick_flow, f"missing primary quick-flow markers: {missing_quick_flow}"

for element_id in ["batchName", "deviceId", "storeKey", "machineCode", "commodityCode", "slot", "sku"]:
    assert re.search(rf'<input\s+id="{element_id}"[^>]*\sreadonly\s*/?>', html), f"identifier must be readonly: {element_id}"

required_redaction_markers = [
    "SYNTHETIC_PATTERNS",
    "setupIsSynthetic",
    "canonicalSetup",
    "SYNTHETIC_ALLOWLIST_BLOCKED",
    "EXPORT_BLOCKED_NON_SYNTHETIC_OR_UNSTAMPED",
    "machine_ref:'SYNTHETIC_MACHINE'",
    "store_ref:'SYNTHETIC_STORE'",
    "commodity_ref:'SYNTHETIC_COMMODITY'",
    "setup:canonicalSetup",
    "runRuntimeSelfTest",
    "hostile_identifier_blocked",
]
missing_redaction = [marker for marker in required_redaction_markers if marker not in html]
assert not missing_redaction, f"missing fail-closed redaction markers: {missing_redaction}"
assert "setup:{...state.setup" not in html, "raw setup spread must not enter results or exports"

required_accessibility_markers = [
    'class="skip-link"',
    ":focus-visible",
    'aria-live="polite"',
    'aria-live="assertive"',
    'aria-atomic="true"',
    'role="status"',
    'role="alert"',
    'aria-describedby="longErrorDetail"',
    '<caption class="sr-only"',
    'id="result-title" tabindex="-1"',
    "longErrorText",
    "queryParams.get('fixture')==='long-error'",
    "runSuite(['malformed_json'])",
    "overflow-wrap: anywhere",
    "@media (max-width: 620px)",
    "prefers-reduced-motion",
]
missing_accessibility = [marker for marker in required_accessibility_markers if marker not in html]
assert not missing_accessibility, f"missing accessibility/RWD markers: {missing_accessibility}"

required_template_metadata = [
    "T7-BUILD-METADATA-02",
    "page_revision: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "content_source_revision: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "parent: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "evidence_commit: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "metadata_binding_commit: 'UNSTAMPED_SOURCE_TEMPLATE'",
    "stamped: false",
    "exit_code: 3",
    "rollback: '6ee1b866e4e07c35800521f67834f1be647c4bbd'",
    "formal_connections: false",
    "real_api_query_count: 0",
    "formal_device_control: false",
    "formal_inventory_write: false",
    "test_device_verified: false",
    "gate_06: 'BLOCKED'",
]
missing_template_metadata = [marker for marker in required_template_metadata if marker not in metadata]
assert not missing_template_metadata, f"missing source template metadata: {missing_template_metadata}"

required_builder_markers = [
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
]
missing_builder = [marker for marker in required_builder_markers if marker not in build_script]
assert not missing_builder, f"missing build provenance markers: {missing_builder}"

report = {
    "status": "PASS",
    "mode": "DEMO_MOCK",
    "evidence_level": "MOCK",
    "schema_version": "T7-VENDOR-SYNTHETIC-03",
    "scenario_count": len(scenario_ids),
    "locales": expected_locales,
    "source_metadata_mode": "UNSTAMPED_FAIL_CLOSED_TEMPLATE",
    "build_artifact_stamps_git_head": True,
    "identifier_redaction": "ALLOWLIST_AND_CANONICAL_REDACTION",
    "primary_quick_flow": ["load_synthetic", "run_all_mock", "view_results", "export_report"],
    "long_error_fixture": "malformed_json",
    "formal_connections": False,
    "real_api_query_count": 0,
    "formal_device_control": False,
    "formal_inventory_write": False,
    "test_device_verified": False,
    "gate_06": "BLOCKED",
    "external_runtime_connections": [],
    "credential_dom_paths": [],
}
print(json.dumps(report, ensure_ascii=False, indent=2))
