#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "t7-test" / "index.html"
METADATA = ROOT / "t7-test" / "build-metadata.js"

html = HTML.read_text(encoding="utf-8")
metadata = METADATA.read_text(encoding="utf-8")

required_ids = {
    "locale",
    "saveSetupBtn",
    "selectAllBtn",
    "runSelectedBtn",
    "runAllBtn",
    "exportJsonBtn",
    "exportCsvBtn",
    "clearBtn",
    "scenarioGrid",
    "resultRows",
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
assert not re.search(r"https?://", html, re.IGNORECASE), "HTML must not contain external URLs"

locale_values = re.findall(r'<option\s+value="([^"]+)">', html)
expected_locales = ["zh-Hant-TW", "en-US", "th-TH", "ja-JP", "id-ID"]
assert locale_values[:5] == expected_locales, f"locale set/order mismatch: {locale_values[:5]}"
for locale in expected_locales:
    assert f"'{locale}':" in html, f"missing translation dictionary: {locale}"

scenario_ids = re.findall(r"\['([a-z0-9_]+)','(?:PASS|ATTENTION|BLOCKED)'", html)
expected_scenarios = {
    "happy_path",
    "fixed_info_report",
    "idempotency_replay",
    "duplicate_callback",
    "qr_invalid",
    "qr_expired",
    "door_blocked",
    "door_unknown",
    "goods_lock_conflict",
    "pickup_unknown",
    "inventory_empty",
    "network_offline",
    "temperature_attention",
    "lane_jam",
    "http_timeout",
    "http_non_2xx",
    "api_state_error",
    "malformed_json",
    "company_scope_mismatch",
    "machine_not_found",
    "commodity_not_found",
    "mapping_conflict",
    "payload_mismatch",
    "partial_dispense",
}
assert len(scenario_ids) == 24, f"scenario count must be 24, got {len(scenario_ids)}"
assert set(scenario_ids) == expected_scenarios, "scenario IDs do not match the approved P2 set"

required_contract_markers = [
    "T7-VENDOR-SYNTHETIC-02",
    "source_revision",
    "evidence_commit",
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

required_accessibility_markers = [
    'class="skip-link"',
    ':focus-visible',
    'aria-live="polite"',
    'role="status"',
    '<caption class="sr-only"',
    'id="result-title" tabindex="-1"',
    '@media (max-width: 620px)',
    'prefers-reduced-motion',
]
missing_accessibility = [marker for marker in required_accessibility_markers if marker not in html]
assert not missing_accessibility, f"missing accessibility/RWD markers: {missing_accessibility}"

revision_matches = re.findall(r"(?:source_revision|evidence_commit):\s*'([0-9a-f]{40})'", metadata)
assert len(revision_matches) == 2, "build metadata must bind source_revision and evidence_commit to 40-character SHAs"
assert "rollback: '6ee1b866e4e07c35800521f67834f1be647c4bbd'" in metadata
assert "formal_connections: false" in metadata
assert "real_api_query_count: 0" in metadata
assert "formal_device_control: false" in metadata
assert "formal_inventory_write: false" in metadata
assert "test_device_verified: false" in metadata
assert "gate_06: 'BLOCKED'" in metadata

report = {
    "status": "PASS",
    "mode": "DEMO_MOCK",
    "evidence_level": "MOCK",
    "scenario_count": len(scenario_ids),
    "locales": expected_locales,
    "source_revision": revision_matches[0],
    "evidence_commit": revision_matches[1],
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
