---
name: fabric-release-verify
description: Verify Microsoft Fabric releases with reproducible evidence. Use after a Fabric Git synchronization, deployment-pipeline promotion, semantic-model update, notebook or pipeline change, or when a user asks to prove that a Fabric deployment completed safely and matches the approved commit.
---

# Fabric release verify

Verify the outcome independently of the deployment command.

## Required evidence

Read ../../common/release-evidence-contract.md. Collect:

1. Environment, workspace ID, branch, and intended commit.
2. Fabric Git status before and after sync.
3. Fabric operation ID and terminal state.
4. Repository validation and test outcomes.
5. Relevant smoke, parity, schema, refresh, or semantic checks.
6. Azure DevOps environment approval and pipeline run links.

## Verification rules

- Fail verification if the remote commit differs from the approved commit.
- Fail verification if the Fabric operation is not in a successful terminal state.
- Escalate if a smoke check is unavailable for a high-risk change.
- Treat RLS, OLS, identities, data-source changes, refresh schedules, and schema deletions as explicit checks, not assumptions.
- Do not mark a release successful merely because the pipeline command exited successfully.

## Output

Append a concise, sanitized verification summary to the evidence package: pass, fail, or escalate; proof used; remaining uncertainty; and the recovery owner. Route an operational issue to ../support-incident-triage/SKILL.md.
