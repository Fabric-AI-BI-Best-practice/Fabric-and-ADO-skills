#!/usr/bin/env python3
"""Create a minimal, sanitized support-incident packet."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--incident-id", required=True)
    parser.add_argument("--severity", required=True, choices=("Sev1", "Sev2", "Sev3", "Sev4"))
    parser.add_argument("--environment", required=True)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--sanitized-summary", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pipeline-run", default="")
    parser.add_argument("--fabric-operation-id", default="")
    parser.add_argument("--owner", default="unassigned")
    args = parser.parse_args()

    if "-----BEGIN" in args.sanitized_summary or "://" in args.sanitized_summary:
        parser.error("Use a sanitized summary without private-key material or raw URLs.")

    packet = {
        "incidentId": args.incident_id,
        "severity": args.severity,
        "timestampUtc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "environment": args.environment,
        "workspaceId": args.workspace_id,
        "summary": args.sanitized_summary,
        "owner": args.owner,
        "pipelineRun": args.pipeline_run or None,
        "fabricOperationId": args.fabric_operation_id or None,
        "status": "triage",
        "nextAction": "Attach authorized log links, confirm severity, and follow the assigned runbook.",
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"[PASS] Wrote sanitized support packet: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
