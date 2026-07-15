# Fabric and ADO agent guide

Use this file as the repository router for Codex, Claude Code, and other coding agents.

## Non-negotiable rules

1. Resolve the repository, branch, Fabric workspace, Azure DevOps environment, identity, and desired action before mutating anything.
2. Treat dev, test, and main as release branches only after the organization maps them to dedicated workspaces. Do not assume that mapping.
3. Read [common/environment-contract.md](common/environment-contract.md) before a deployment and [common/release-evidence-contract.md](common/release-evidence-contract.md) before approving one.
4. Do not send secrets, personal data, customer data, unredacted logs, or workspace exports to an external model.
5. Treat Fabric workspace conflicts as a stop condition. Do not use a remote-override option until the change owner and environment gate explicitly approve it.
6. Produce an evidence package for every release attempt, including failed or blocked attempts.
7. AI review is advisory. Only deterministic controls and named human approvers can authorize a production deployment.

## Route the task

| User intent | Read first |
| --- | --- |
| Plan a Fabric change | [skills/fabric-change-plan/SKILL.md](skills/fabric-change-plan/SKILL.md) |
| Bring a workspace up to its Git branch | [skills/fabric-git-sync/SKILL.md](skills/fabric-git-sync/SKILL.md) |
| Build or run a governed Azure DevOps release | [skills/ado-fabric-release/SKILL.md](skills/ado-fabric-release/SKILL.md) |
| Validate a release after deployment | [skills/fabric-release-verify/SKILL.md](skills/fabric-release-verify/SKILL.md) |
| Triage a support incident | [skills/support-incident-triage/SKILL.md](skills/support-incident-triage/SKILL.md) |
| Cross-check an evidence package with models | [skills/ai-release-review/SKILL.md](skills/ai-release-review/SKILL.md) |

## Standard run workspace

Keep run outputs out of source-controlled item definitions:

~~~text
out/
  <release-or-incident-id>/
    01-plan.md
    02-validation.json
    03-release-evidence.json
    04-ai-review-<reviewer>.json
    05-verification.md
~~~

The out directory is ignored by Git. Upload only sanitized evidence artifacts to the pipeline run or work item.

## Required response format

For any action that could modify Fabric or Azure DevOps, report:

- Target: environment, workspace ID, branch, and commit.
- Authority: identity and named approval or check that authorizes the action.
- Plan: exact command or pipeline stage, with dry-run status.
- Evidence: validation outputs, Fabric operation ID, and verification result.
- Recovery: rollback or containment action if the operation fails.

If any field is missing, remain read-only and ask for it.
