#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
SNAPSHOT = ROOT / "evidence" / "t7-self-service-browser-snapshot-20260831.json"
JSON_EXPORT = ROOT / "evidence" / "t7-self-service-full-suite-sample-20260831.json"
CSV_EXPORT = ROOT / "evidence" / "t7-self-service-full-suite-sample-20260831.csv"
CONFIG = ROOT / "config.js"

html = HTML.read_text(encoding="utf-8")
config = CONFIG.read_text(encoding="utf-8")
snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
json_export = json.loads(JSON_EXPORT.read_text(encoding="utf-8"))
with CSV_EXPORT.open(encoding="utf-8-sig", newline="") as handle:
    csv_rows = list(csv.DictReader(handle))

required_markers = [
    "自助式測試工作台",
    "saveSetupBtn",
    "runSelectedSuiteBtn",
    "runFullSuiteBtn",
    "exportJsonBtn",
    "exportCsvBtn",
    "completion_signal: false",
    "gate_06: 'BLOCKED'",
    "realPreflightBtn",
    "testerAccessKey",
    "managerAccessKey",
    "saveCredentialBtn",
    "rollbackCredentialBtn",
    "READ_ONLY_TEST_ADAPTER",
    "./config.js",
]
for marker in required_markers:
    assert marker in html, f"missing HTML marker: {marker}"

scenario_ids = [
    "happy_path",
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
    "fixed_info_report",
]
for scenario_id in scenario_ids:
    assert scenario_id in html, f"missing scenario: {scenario_id}"

for forbidden in [
    r"XMLHttpRequest",
    r"WebSocket",
    r"localStorage",
    r"sessionStorage",
    r"indexedDB",
    r"navigator\.sendBeacon",
]:
    assert not re.search(forbidden, html, re.IGNORECASE), f"forbidden runtime API: {forbidden}"

assert html.count("fetch(") == 1, "only the guarded Adapter fetch is allowed"
assert "adapterBaseUrl" in config
assert "2000162" not in config
assert "token" not in config.lower()
assert "access_key" not in config.lower()
assert "T7_TESTER_ACCESS_KEY" not in html
assert "T7_MANAGER_ACCESS_KEY" not in html
assert "TIANLAI_TOKEN" not in html

assert snapshot["status"] == "SELF_SERVICE_BROWSER_SMOKE_PASS_SIMULATOR_ONLY"
assert snapshot["mode"] == "DEMO_MOCK"
assert snapshot["completion_signal"] is False
assert snapshot["scenario_count"] == 12
assert snapshot["gate"]["status"] == "BLOCKED"
assert snapshot["safety"]["external_api_called"] is False
assert snapshot["safety"]["formal_device_control"] is False
assert snapshot["safety"]["formal_inventory_write"] is False
assert snapshot["safety"]["direct_refund"] is False
assert snapshot["safety"]["unknown_auto_resend"] is False

assert len(json_export["outputs"]) == 12
assert len(csv_rows) == 12

sensitive_keys = {"company", "customer_code", "token", "sign", "password"}
redacted_values = {"OMITTED", "[OMITTED]", "REDACTED", "[REDACTED]", "REDACTED_NOT_EXPORTED", "NOT_EXPORTED", "", None}


def assert_sensitive_values_redacted(value: object) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.lower() in sensitive_keys:
                assert nested in redacted_values, f"sensitive field is not redacted: {key}"
            assert_sensitive_values_redacted(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_sensitive_values_redacted(nested)


assert_sensitive_values_redacted(json_export)
assert not any(key.lower() in sensitive_keys for row in csv_rows for key in row)

print("static_site_validation=PASS")
print("scenario_count=12")
print("json_outputs=12")
print("csv_rows=12")
print("external_runtime_connections=READ_ONLY_ADAPTER_ONLY")
print("formal_device_control=false")
print("completion_signal=false")
print("gate_06=BLOCKED")
