# Release evidence contract

A release package proves what was proposed, checked, approved, deployed, and observed. It is not a dump of raw logs.

## Minimum evidence

| Field | Why it matters |
| --- | --- |
| releaseId, timestampUtc | Links records across pipeline, work item, and monitoring |
| environment, workspaceId, sourceBranch, commit | Makes the target and source unambiguous |
| riskLevel, changeSummary | Captures change intent and impact |
| validations | Records deterministic check results |
| approvals | Records resource approval or explains why it was not needed |
| fabricOperation | Stores the Fabric operation ID and final status when deployment runs |
| verification | Captures smoke, parity, and semantic checks |
| recoveryPlan | Identifies containment or rollback action |

Use [templates/release-evidence.schema.json](../templates/release-evidence.schema.json) and validate with [scripts/validate_release_evidence.py](../scripts/validate_release_evidence.py).

The contract is intentionally closed: undeclared fields and common credential-bearing values are rejected so an evidence package cannot gradually become a raw-log archive.

## Evidence hygiene

- Replace display names, row-level values, query text, URLs containing credentials, and access tokens with safe identifiers before attaching evidence.
- Link to an authorized internal log location instead of embedding sensitive logs.
- Preserve the original evidence in the authorized system of record; do not alter an approved record without appending a correction.
