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
TEXT_SCAN_CHUNK_SIZE = 64 * 1024
TEXT_SCAN_OVERLAP = 512
MAX_JSON_PARSE_BYTES = 10 * 1024 * 1024
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


def check_text_for_secrets(path: Path, relative: Path, errors: list[str]) -> bool:
    """Scan UTF-8 text incrementally so large artifacts are never exempt from secret checks."""
    try:
        with path.open("r", encoding="utf-8") as source:
            tail = ""
            found_private_key = False
            found_assignment = False
            while chunk := source.read(TEXT_SCAN_CHUNK_SIZE):
                text = tail + chunk
                if not found_private_key and PRIVATE_KEY_PATTERN.search(text):
                    errors.append(f"{relative}: private-key material detected")
                    found_private_key = True
                if not found_assignment and SECRET_ASSIGNMENT_PATTERN.search(text):
                    errors.append(f"{relative}: possible inline secret assignment detected")
                    found_assignment = True
                tail = text[-TEXT_SCAN_OVERLAP:]
    except UnicodeDecodeError:
        return False
    return True


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
        relative = path.relative_to(root)
        if not check_text_for_secrets(path, relative, errors):
            if args.require_fabric_items and fabric_root in path.parents:
                errors.append(f"{relative}: unable to scan Fabric artifact as UTF-8 text")
            else:
                warnings.append(f"{relative}: skipped secret scan because file is not UTF-8 text")
            continue
        if path.suffix.lower() in JSON_EXTENSIONS:
            if path.stat().st_size > MAX_JSON_PARSE_BYTES:
                warnings.append(
                    f"{relative}: skipped JSON syntax validation because file exceeds "
                    f"{MAX_JSON_PARSE_BYTES // (1024 * 1024)} MB; secret scan still ran"
                )
            else:
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
