#!/usr/bin/env python3
"""Run dependency-free structural and secret-pattern checks on a Fabric repository."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SKIP_DIRECTORIES = {".git", ".venv", "__pycache__", "out", "node_modules"}
JSON_EXTENSIONS = {".json", ".platform", ".ipynb"}
PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(?:client[_-]?secret|password|api[_-]?key|access[_-]?token|connection[_-]?string)"
    r"\b\s*[:=]\s*[\"']?(?!<|\$\(|\{\{)[^\s\"']{8,}"
)


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRECTORIES for part in path.parts)


def check_json(path: Path, errors: list[str]) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        errors.append(f"{path}: expected UTF-8 JSON-compatible text")
    except json.JSONDecodeError as error:
        errors.append(f"{path}: invalid JSON-compatible file: {error.msg} at line {error.lineno}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to inspect.")
    parser.add_argument(
        "--require-fabric-items",
        action="store_true",
        help="Fail when fabric/ contains no deployable item definitions.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    fabric_root = root / "fabric"
    if not fabric_root.is_dir():
        errors.append(f"{fabric_root}: missing fabric item-definition directory")
    else:
        item_files = [
            path
            for path in fabric_root.rglob("*")
            if path.is_file() and path.suffix.lower() not in {".md", ".txt"}
        ]
        if args.require_fabric_items and not item_files:
            errors.append("fabric/: no deployable item-definition files found")
        elif not item_files:
            warnings.append("fabric/: no deployable item-definition files found; template mode is active")

    for path in root.rglob("*"):
        if not path.is_file() or is_skipped(path.relative_to(root)):
            continue
        if path.stat().st_size > 1_000_000:
            warnings.append(f"{path.relative_to(root)}: skipped secret scan because file exceeds 1 MB")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(root)
        if PRIVATE_KEY_PATTERN.search(text):
            errors.append(f"{relative}: private-key material detected")
        if SECRET_ASSIGNMENT_PATTERN.search(text):
            errors.append(f"{relative}: possible inline secret assignment detected")
        if path.suffix.lower() in JSON_EXTENSIONS:
            check_json(path, errors)

    for warning in warnings:
        print(f"[WARN] {warning}")
    if errors:
        print(f"[FAIL] Found {len(errors)} problem(s):")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("[PASS] Repository structure and lightweight secret scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
