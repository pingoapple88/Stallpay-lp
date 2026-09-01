from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "t7-test" / "index.html"
CONFIG = ROOT / "t7-test" / "config.js"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    html = PAGE.read_text(encoding="utf-8")
    config = CONFIG.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    required_ids = {
        "quickRunBtn",
        "quickClearBtn",
        "quickExportBtn",
        "quickStatus",
        "self-service-title",
        "runFullSuiteBtn",
        "exportJsonBtn",
        "realPreflightBtn",
        "saveCredentialBtn",
        "rollbackCredentialBtn",
    }
    actual_ids = {node.get("id") for node in soup.find_all(id=True)}
    missing_ids = sorted(required_ids - actual_ids)
    if missing_ids:
        fail(f"missing required ids: {missing_ids}")

    for element_id in required_ids:
        if len(soup.find_all(id=element_id)) != 1:
            fail(f"id is not unique: {element_id}")

    required_copy = [
        "DEMO_MOCK",
        "formal_device_control",
        "formal_inventory_write",
        "GATE-06",
        "completion_signal",
        "繁中",
        "English",
        "ไทย",
        "日本語",
        "Bahasa",
        "下載測試報告",
    ]
    for marker in required_copy:
        if marker not in html:
            fail(f"missing safety or usability marker: {marker}")

    forbidden_markers = ["forge.manus.im", "vite-plugin-manus-runtime", "localStorage.setItem('manus-", "localStorage.setItem(\"manus-"]
    for marker in forbidden_markers:
        if marker in html or marker in config:
            fail(f"forbidden platform marker found: {marker}")

    endpoint_literals = sorted(set(re.findall(r"adapterFetch\(['\"]([^'\"]+)['\"]", html)))
    allowed_endpoints = {
        "/healthz",
        "/api/v1/t7/network/preflight",
        "/api/v1/t7/settings/status",
        "/api/v1/t7/settings",
        "/api/v1/t7/settings/rollback",
    }
    unexpected = [item for item in endpoint_literals if item.startswith("/") and item not in allowed_endpoints]
    if unexpected:
        fail(f"unexpected adapter endpoint literals: {unexpected}")

    if "adapterBaseUrl: \"https://" not in config:
        fail("adapterBaseUrl is not an explicit HTTPS URL")
    if "adapterBaseUrl: \"http://" in config:
        fail("insecure HTTP adapter URL")

    inline_scripts = soup.find_all("script")
    if not inline_scripts:
        fail("no inline script found")
    script_body = inline_scripts[-1].get_text()
    syntax_path = Path("/home/ubuntu/work/t7_site_inline_syntax_check.js")
    syntax_path.write_text(script_body, encoding="utf-8")
    result = subprocess.run(["node", "--check", str(syntax_path)], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="")
        fail("inline JavaScript syntax check failed")

    report = {
        "status": "PASS",
        "page": str(PAGE),
        "quick_flow": ["load_synthetic", "run_mock_suite", "view_results", "export_report"],
        "required_ids_checked": sorted(required_ids),
        "unexpected_endpoint_literals": [],
        "formal_api_called_by_static_check": False,
        "formal_device_control": False,
        "formal_inventory_write": False,
        "real_api_query_count": 0,
        "node_syntax_exit_code": result.returncode,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
