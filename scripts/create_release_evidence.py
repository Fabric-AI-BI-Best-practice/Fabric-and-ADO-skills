#!/usr/bin/env python3
"""Create a release-evidence record without embedding secrets or raw logs."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _load_sync_result(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {
            "operationId": None,
            "status": "not-run",
            "details": "No Fabric sync result was supplied.",
        }
    result = json.loads(path.read_text(encoding="utf-8"))
    status = str(result.get("operationStatus", "unknown")).lower()
    if status == "completed":
        status = "succeeded"
    if status not in {"not-run", "planned", "running", "succeeded", "failed", "unknown"}:
        status = "unknown"
    return {
        "operationId": result.get("operationId"),
        "status": status,
        "details": (
            f"Mode={result.get('mode', 'unknown')}; "
            f"remoteCommitHash={result.get('remoteCommitHash', 'unknown')}; "
            f"changeCount={result.get('changeCount', 'unknown')}"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--source-branch", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--risk-level", required=True, choices=("low", "moderate", "high"))
    parser.add_argument("--change-summary", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pipeline-run", default="")
    parser.add_argument("--sync-result", type=Path)
    parser.add_argument("--validation-name", default="pipeline-validation")
    parser.add_argument(
        "--validation-status",
        default="pending",
        choices=("pending", "passed", "failed", "skipped"),
    )
    parser.add_argument("--approval-kind", default="environment-gate")
    parser.add_argument(
        "--approval-status",
        default="pending",
        choices=("pending", "approved", "rejected", "not-required"),
    )
    parser.add_argument("--recovery-plan", default="Stop promotion and follow the approved recovery owner.")
    args = parser.parse_args()

    record: dict[str, Any] = {
        "releaseId": args.release_id,
        "timestampUtc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "environment": args.environment,
        "workspaceId": args.workspace_id,
        "sourceBranch": args.source_branch,
        "commit": args.commit,
        "riskLevel": args.risk_level,
        "changeSummary": args.change_summary,
        "validations": [
            {
                "name": args.validation_name,
                "status": args.validation_status,
                "evidence": "See the associated Azure DevOps pipeline run.",
            }
        ],
        "approvals": [
            {
                "kind": args.approval_kind,
                "status": args.approval_status,
                "reference": args.pipeline_run or "Not supplied",
            }
        ],
        "fabricOperation": _load_sync_result(args.sync_result),
        "verification": {
            "status": "pending",
            "checks": [
                {
                    "name": "post-deploy-verification",
                    "status": "pending",
                    "evidence": "Complete the change-specific smoke and parity checks.",
                }
            ],
        },
        "recoveryPlan": args.recovery_plan,
    }
    if args.pipeline_run:
        record["pipelineRun"] = args.pipeline_run

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"[PASS] Wrote release evidence: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
