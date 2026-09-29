#!/usr/bin/env python3
"""Build a public, source-free Xiaoxianji static site for Cloudflare Pages."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROLLBACK = "6ee1b866e4e07c35800521f67834f1be647c4bbd"
PUBLIC_ROOT_FILES = ("index.html", "og-image.jpg")


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def metadata_javascript(metadata: dict[str, object]) -> str:
    lines = ["window.XIAOXIANJI_BUILD_METADATA = Object.freeze({"]
    for key, value in metadata.items():
        lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)},")
    lines.append("});")
    return "\n".join(lines) + "\n"


def copy_site(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for filename in PUBLIC_ROOT_FILES:
        source = REPO / filename
        if source.exists():
            shutil.copy2(source, output / filename)

    uat_output = output / "uat"
    uat_output.mkdir()
    shutil.copy2(REPO / "backend" / "frontend" / "index.html", uat_output / "index.html")
    (uat_output / "config.js").write_text(
        'window.XIAOXIANJI_UAT_CONFIG = Object.freeze({mode:"STATIC_SANDBOX",apiBaseUrl:null});\n',
        encoding="utf-8",
    )
    (output / "_headers").write_text(
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.xiaoxianji.merchcore.ai; base-uri 'self'; form-action 'self'\n",
        encoding="utf-8",
    )


def parent_revision(head: str) -> str:
    try:
        parent = git("rev-parse", "HEAD^")
        if parent:
            return parent
    except subprocess.CalledProcessError:
        pass
    fetched = subprocess.run(
        ["git", "fetch", "--no-tags", "--depth=2", "origin", head],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    if fetched.returncode != 0:
        raise SystemExit("PARENT_REVISION_UNAVAILABLE")
    try:
        parent = git("rev-parse", "HEAD^")
    except subprocess.CalledProcessError as exc:
        raise SystemExit("PARENT_REVISION_UNAVAILABLE") from exc
    if len(parent) != 40:
        raise SystemExit("PARENT_REVISION_INVALID")
    return parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the source-free Xiaoxianji public site.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if git("diff", "--name-only") or git("diff", "--cached", "--name-only"):
        raise SystemExit("TRACKED_WORKTREE_MUST_BE_CLEAN_BEFORE_STAMPING")
    head = git("rev-parse", "HEAD")
    parent = parent_revision(head)
    branch = git("branch", "--show-current") or "DETACHED_HEAD"
    if len(head) != 40 or len(parent) != 40:
        raise SystemExit("INVALID_GIT_REVISION")
    output = args.output.resolve()
    if output == REPO or REPO in output.parents and output.name != "dist":
        raise SystemExit("OUTPUT_MUST_BE_DIST_OR_OUTSIDE_REPO")
    copy_site(output)
    metadata: dict[str, object] = {
        "schema_version": "XJ-BUILD-METADATA-01",
        "page_revision": head,
        "parent": parent,
        "rollback": ROLLBACK,
        "branch": branch,
        "stamped": True,
        "mode": "DEMO_MOCK",
        "formal_connections": False,
        "public_source_whitelist": True,
    }
    metadata_dir = output / "_build"
    metadata_dir.mkdir()
    (metadata_dir / "build-metadata.js").write_text(metadata_javascript(metadata), encoding="utf-8")
    (metadata_dir / "BUILD_PROVENANCE.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "output": str(output), **metadata}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
