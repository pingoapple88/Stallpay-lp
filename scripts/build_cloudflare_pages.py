#!/usr/bin/env python3
"""Build the complete static site with a stamped T7 test artifact for Cloudflare."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROLLBACK = "6ee1b866e4e07c35800521f67834f1be647c4bbd"
EXCLUDED_DIRS = {".git", "dist", "__pycache__", ".pytest_cache", ".mypy_cache"}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def metadata_javascript(metadata: dict[str, object]) -> str:
    lines = ["window.T7_BUILD_METADATA = Object.freeze({"]
    for key, value in metadata.items():
        lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)},")
    lines.append("});")
    return "\n".join(lines) + "\n"


def copy_site(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for source in REPO.iterdir():
        if source.name in EXCLUDED_DIRS:
            continue
        target = output / source.name
        if source.is_dir():
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns(
                    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", "dist"
                ),
            )
        else:
            shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the complete Cloudflare static site with stamped T7 metadata."
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if git("diff", "--name-only") or git("diff", "--cached", "--name-only"):
        raise SystemExit("TRACKED_WORKTREE_MUST_BE_CLEAN_BEFORE_STAMPING")

    head = git("rev-parse", "HEAD")
    parent = git("rev-parse", "HEAD^")
    branch = git("branch", "--show-current") or "DETACHED_HEAD"
    if len(head) != 40 or len(parent) != 40:
        raise SystemExit("INVALID_GIT_REVISION")

    output = args.output.resolve()
    if output == REPO or REPO in output.parents and output.name != "dist":
        raise SystemExit("OUTPUT_MUST_BE_DIST_OR_OUTSIDE_REPO")

    copy_site(output)
    metadata: dict[str, object] = {
        "schema_version": "T7-BUILD-METADATA-02",
        "page_revision": head,
        "content_source_revision": head,
        "parent": parent,
        "evidence_commit": head,
        "metadata_binding_commit": head,
        "rollback": ROLLBACK,
        "branch": branch,
        "stamped": True,
        "exit_code": 0,
        "mode": "DEMO_MOCK",
        "evidence_level": "MOCK",
        "formal_connections": False,
        "real_api_query_count": 0,
        "formal_device_control": False,
        "formal_inventory_write": False,
        "test_device_verified": False,
        "gate_06": "BLOCKED",
    }
    metadata_path = output / "t7-test" / "build-metadata.js"
    metadata_path.write_text(metadata_javascript(metadata), encoding="utf-8")
    (output / "t7-test" / "BUILD_PROVENANCE.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "output": str(output), **metadata}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
