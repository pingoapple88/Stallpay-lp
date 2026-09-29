#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ALLOWED_TOP_LEVEL = {"index.html", "og-image.jpg", "uat", "_headers", "_build"}
FORBIDDEN_TEXT = ("temporary_url", "BEGIN PRIVATE KEY", "INTELLA_TRANSACTION_PASSWORD=")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the source-free Xiaoxianji public build.")
    parser.add_argument("build_dir", type=Path)
    args = parser.parse_args()
    root = args.build_dir.resolve()
    if not root.is_dir():
        raise SystemExit("BUILD_DIR_NOT_FOUND")
    names = {item.name for item in root.iterdir()}
    unexpected = names - ALLOWED_TOP_LEVEL
    if unexpected:
        raise SystemExit(f"UNEXPECTED_PUBLIC_PATHS:{','.join(sorted(unexpected))}")
    required = (root / "index.html", root / "uat" / "index.html", root / "uat" / "config.js", root / "_headers")
    if any(not path.is_file() for path in required):
        raise SystemExit("REQUIRED_PUBLIC_FILE_MISSING")
    if "STATIC_SANDBOX" not in (root / "uat" / "config.js").read_text(encoding="utf-8"):
        raise SystemExit("STATIC_UAT_CONFIG_MISSING")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in FORBIDDEN_TEXT:
            if marker.lower() in text.lower():
                raise SystemExit(f"FORBIDDEN_PUBLIC_MARKER:{marker}:{path.relative_to(root)}")
    print("PUBLIC_BUILD_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
