#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
CONFIG = ROOT / "config.js"
METADATA = ROOT / "build-metadata.js"

html = HTML.read_text(encoding="utf-8")
config = CONFIG.read_text(encoding="utf-8")
metadata = METADATA.read_text(encoding="utf-8")

required_markers = [
    "智販機 Synthetic 測試工作台",
    "T7-VENDOR-SYNTHETIC-02",
    "saveSetupBtn",
    "runSelectedBtn",
    "runAllBtn",
    "exportJsonBtn",
    "exportCsvBtn",
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
    "aria-live=\"polite\"",
    ":focus-visible",
    "prefers-reduced-motion",
]
for marker in required_markers:
    assert marker in html, f"missing HTML marker: {marker}"

for forbidden_id in [
    "realPreflightBtn",
    "adapterHealthBtn",
    "testerAccessKey",
    "managerAccessKey",
    "managerToken",
    "loadCredentialStatusBtn",
    "saveCredentialBtn",
    "rollbackCredentialBtn",
]:
    assert f'id="{forbidden_id}"' not in html, f"forbidden DOM path remains: {forbidden_id}"

for forbidden_runtime in [
    r"\bfetch\s*\(",
    r"(?:new\s+)?XMLHttpRequest\s*\(",
    r"(?:new\s+)?WebSocket\s*\(",
    r"(?:navigator\.)?sendBeacon\s*\(",
    r"localStorage",
    r"sessionStorage",
    r"indexedDB",
    r"/api/v1/t7/network/preflight",
    r"/api/v1/t7/settings",
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
    assert f"value=\"{locale}\"" in html
    assert f"'{locale}':" in html

scenario_ids = re.findall(r"\['([a-z0-9_]+)','(?:PASS|ATTENTION|BLOCKED)'", html)
assert len(scenario_ids) == 24, f"scenario count must be 24, got {len(scenario_ids)}"
assert len(set(scenario_ids)) == 24, "scenario IDs must be unique"

revision_matches = re.findall(r"(?:source_revision|evidence_commit):\s*'([0-9a-f]{40})'", metadata)
assert len(revision_matches) == 2, "source/evidence revision is not bound to 40-character SHAs"
assert "rollback: '6ee1b866e4e07c35800521f67834f1be647c4bbd'" in metadata
assert "real_api_query_count: 0" in metadata
assert "formal_device_control: false" in metadata
assert "formal_inventory_write: false" in metadata
assert "test_device_verified: false" in metadata
assert "gate_06: 'BLOCKED'" in metadata

for secret_pattern in [
    r"Bearer\s+[A-Za-z0-9._-]{12,}",
    r"AKIA[A-Z0-9]{16}",
    r"sk-[A-Za-z0-9]{16,}",
    r"-----BEGIN\s+.*PRIVATE\s+KEY-----",
]:
    assert not re.search(secret_pattern, html + config + metadata), f"secret pattern found: {secret_pattern}"

print("static_site_validation=PASS")
print("scenario_count=24")
print("locales=zh-Hant-TW,en-US,th-TH,ja-JP,id-ID")
print("external_runtime_connections=NONE")
print("credential_dom_paths=NONE")
print("formal_connections=false")
print("real_api_query_count=0")
print("formal_device_control=false")
print("formal_inventory_write=false")
print("test_device_verified=false")
print("gate_06=BLOCKED")
