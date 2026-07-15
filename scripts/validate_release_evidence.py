#!/usr/bin/env python3
"""Validate a sanitized Fabric and Azure DevOps release-evidence record."""

from __future__ import annotations

import argparse
import json
import re
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
ALLOWED_TOP_LEVEL_FIELDS = {
    "releaseId",
    "timestampUtc",
    "environment",
    "workspaceId",
    "sourceBranch",
    "commit",
    "riskLevel",
    "changeSummary",
    "pipelineRun",
    "validations",
    "approvals",
    "fabricOperation",
    "verification",
    "recoveryPlan",
}
ALLOWED_VALIDATION_FIELDS = {"name", "status", "evidence"}
ALLOWED_APPROVAL_FIELDS = {"kind", "status", "reference"}
ALLOWED_OPERATION_FIELDS = {"operationId", "status", "details"}
ALLOWED_VERIFICATION_FIELDS = {"status", "checks"}
ALLOWED_CHECK_FIELDS = {"name", "status", "evidence"}
PRIVATE_KEY_VALUE_PATTERN = re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")
SECRET_ASSIGNMENT_VALUE_PATTERN = re.compile(
    r"(?i)\b(?:client[_-]?secret|password|api[_-]?key|access[_-]?token|connection[_-]?string)"
    r"\b\s*[:=]\s*[\"']?(?!<|\$\(|\{\{)[^\s\"']{8,}"
)
BEARER_TOKEN_VALUE_PATTERN = re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]{16,}")
CREDENTIAL_URL_VALUE_PATTERN = re.compile(r"(?i)\bhttps?://[^\s/@:]+:[^@/\s]+@")
SENSITIVE_URL_PARAMETER_PATTERN = re.compile(
    r"(?i)[?&](?:access[_-]?token|token|api[_-]?key|key|sig|signature|password|client[_-]?secret)="
    r"[^&\s]{8,}"
)


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


def find_sensitive_values(value: Any, path: str = "$") -> list[str]:
    """Reject common secret-bearing values before evidence is published."""
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            findings.extend(find_sensitive_values(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_sensitive_values(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        patterns = (
            (PRIVATE_KEY_VALUE_PATTERN, "private-key material"),
            (SECRET_ASSIGNMENT_VALUE_PATTERN, "a secret-like assignment"),
            (BEARER_TOKEN_VALUE_PATTERN, "a bearer token"),
            (CREDENTIAL_URL_VALUE_PATTERN, "a credential-bearing URL"),
            (SENSITIVE_URL_PARAMETER_PATTERN, "a sensitive URL parameter"),
        )
        for pattern, description in patterns:
            if pattern.search(value):
                findings.append(f"{path}: evidence must not contain {description}")
                break
    return findings


def _check_allowed_fields(record: dict[str, Any], allowed: set[str], path: str, errors: list[str]) -> None:
    for field in record:
        if field not in allowed:
            errors.append(f"{path}.{field}: unexpected field")


def _check_optional_text(record: dict[str, Any], field: str, path: str, errors: list[str]) -> None:
    if field in record and not _is_text(record[field]):
        errors.append(f"{path}.{field}: expected a non-empty string")


def validate(record: Any) -> list[str]:
    """Return all structural and safety problems found in a record."""
    if not isinstance(record, dict):
        return ["root: expected a JSON object"]

    errors: list[str] = []
    _check_allowed_fields(record, ALLOWED_TOP_LEVEL_FIELDS, "$", errors)
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
    _check_optional_text(record, "pipelineRun", "$", errors)

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
            _check_allowed_fields(item, ALLOWED_VALIDATION_FIELDS, prefix, errors)
            if not _is_text(item.get("name")):
                errors.append(f"{prefix}.name: expected a non-empty string")
            if item.get("status") not in VALIDATION_STATUSES:
                errors.append(f"{prefix}.status: invalid validation status")
            _check_optional_text(item, "evidence", prefix, errors)

    approvals = record.get("approvals")
    if not isinstance(approvals, list) or not approvals:
        errors.append("approvals: expected a non-empty array")
    else:
        for index, item in enumerate(approvals):
            prefix = f"approvals[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix}: expected an object")
                continue
            _check_allowed_fields(item, ALLOWED_APPROVAL_FIELDS, prefix, errors)
            if not _is_text(item.get("kind")):
                errors.append(f"{prefix}.kind: expected a non-empty string")
            if item.get("status") not in APPROVAL_STATUSES:
                errors.append(f"{prefix}.status: invalid approval status")
            _check_optional_text(item, "reference", prefix, errors)

    operation = record.get("fabricOperation")
    if not isinstance(operation, dict):
        errors.append("fabricOperation: expected an object")
    else:
        _check_allowed_fields(operation, ALLOWED_OPERATION_FIELDS, "fabricOperation", errors)
        if operation.get("status") not in OPERATION_STATUSES:
            errors.append("fabricOperation.status: invalid operation status")
        if "operationId" in operation and operation["operationId"] is not None and not _is_text(operation["operationId"]):
            errors.append("fabricOperation.operationId: expected a non-empty string or null")
        _check_optional_text(operation, "details", "fabricOperation", errors)

    verification = record.get("verification")
    if not isinstance(verification, dict):
        errors.append("verification: expected an object")
    else:
        _check_allowed_fields(verification, ALLOWED_VERIFICATION_FIELDS, "verification", errors)
        if verification.get("status") not in VERIFICATION_STATUSES:
            errors.append("verification.status: invalid verification status")
        checks = verification.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append("verification.checks: expected a non-empty array")
        else:
            for index, item in enumerate(checks):
                prefix = f"verification.checks[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{prefix}: expected an object")
                    continue
                _check_allowed_fields(item, ALLOWED_CHECK_FIELDS, prefix, errors)
                if not _is_text(item.get("name")):
                    errors.append(f"{prefix}.name: expected a non-empty string")
                if item.get("status") not in VALIDATION_STATUSES:
                    errors.append(f"{prefix}.status: invalid check status")
                _check_optional_text(item, "evidence", prefix, errors)

    errors.extend(_check_sensitive_keys(record))
    errors.extend(find_sensitive_values(record))
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
