#!/usr/bin/env python3
"""Validate a sanitized Fabric and Azure DevOps release-evidence record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


RISK_LEVELS = {"low", "moderate", "high"}
VALIDATION_STATUSES = {"pending", "passed", "failed", "skipped"}
APPROVAL_STATUSES = {"pending", "approved", "rejected", "not-required"}
OPERATION_STATUSES = {"not-run", "planned", "running", "succeeded", "failed", "unknown"}
VERIFICATION_STATUSES = {"pending", "passed", "failed", "escalate", "skipped"}
SENSITIVE_KEY_MARKERS = {
    "access_token",
    "accesstoken",
    "api_key",
    "apikey",
    "client_secret",
    "clientsecret",
    "connection_string",
    "connectionstring",
    "password",
    "private_key",
    "secret",
}


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _check_sensitive_keys(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = str(key).replace("-", "_").lower()
            child_path = f"{path}.{key}"
            if lowered in SENSITIVE_KEY_MARKERS:
                findings.append(f"{child_path}: evidence must not contain a sensitive key")
            findings.extend(_check_sensitive_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_check_sensitive_keys(child, f"{path}[{index}]"))
    return findings


def validate(record: Any) -> list[str]:
    """Return all structural and safety problems found in a record."""
    if not isinstance(record, dict):
        return ["root: expected a JSON object"]

    errors: list[str] = []
    required_text = (
        "releaseId",
        "timestampUtc",
        "environment",
        "workspaceId",
        "sourceBranch",
        "commit",
        "changeSummary",
        "recoveryPlan",
    )
    for field in required_text:
        if not _is_text(record.get(field)):
            errors.append(f"{field}: expected a non-empty string")

    if record.get("riskLevel") not in RISK_LEVELS:
        errors.append("riskLevel: expected low, moderate, or high")

    validations = record.get("validations")
    if not isinstance(validations, list) or not validations:
        errors.append("validations: expected a non-empty array")
    else:
        for index, item in enumerate(validations):
            prefix = f"validations[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix}: expected an object")
                continue
            if not _is_text(item.get("name")):
                errors.append(f"{prefix}.name: expected a non-empty string")
            if item.get("status") not in VALIDATION_STATUSES:
                errors.append(f"{prefix}.status: invalid validation status")

    approvals = record.get("approvals")
    if not isinstance(approvals, list):
        errors.append("approvals: expected an array")
    else:
        for index, item in enumerate(approvals):
            prefix = f"approvals[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix}: expected an object")
                continue
            if not _is_text(item.get("kind")):
                errors.append(f"{prefix}.kind: expected a non-empty string")
            if item.get("status") not in APPROVAL_STATUSES:
                errors.append(f"{prefix}.status: invalid approval status")

    operation = record.get("fabricOperation")
    if not isinstance(operation, dict):
        errors.append("fabricOperation: expected an object")
    elif operation.get("status") not in OPERATION_STATUSES:
        errors.append("fabricOperation.status: invalid operation status")

    verification = record.get("verification")
    if not isinstance(verification, dict):
        errors.append("verification: expected an object")
    else:
        if verification.get("status") not in VERIFICATION_STATUSES:
            errors.append("verification.status: invalid verification status")
        checks = verification.get("checks")
        if not isinstance(checks, list):
            errors.append("verification.checks: expected an array")
        else:
            for index, item in enumerate(checks):
                prefix = f"verification.checks[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{prefix}: expected an object")
                    continue
                if not _is_text(item.get("name")):
                    errors.append(f"{prefix}.name: expected a non-empty string")
                if item.get("status") not in VALIDATION_STATUSES:
                    errors.append(f"{prefix}.status: invalid check status")

    errors.extend(_check_sensitive_keys(record))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path, help="Evidence JSON file to validate.")
    args = parser.parse_args()

    try:
        record = json.loads(args.file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[FAIL] Evidence file not found: {args.file}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"[FAIL] Invalid JSON in {args.file}: {error}", file=sys.stderr)
        return 2

    errors = validate(record)
    if errors:
        print(f"[FAIL] {args.file} has {len(errors)} validation problem(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"[PASS] {args.file} is a valid sanitized release-evidence record.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
