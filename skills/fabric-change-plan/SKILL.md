---
name: fabric-change-plan
description: Plan safe Microsoft Fabric changes before editing artifacts or deploying them. Use for requests to change Fabric lakehouses, notebooks, pipelines, semantic models, reports, security, workspace settings, or data contracts, especially when a change needs Azure DevOps promotion, risk assessment, validation, or rollback planning.
---

# Fabric change plan

Create a change plan before modifying a Fabric item or Azure DevOps release definition.

## Gather the minimum context

Resolve the exact environment, workspace ID, connected branch, commit or pull request, Fabric item types, owner, desired business outcome, and recovery owner. Read ../../common/environment-contract.md.

Remain read-only if any target field is unknown. Never guess a production workspace from a display name.

## Classify risk

Use low risk only for reversible documentation or isolated development changes. Use moderate risk for normal item updates with tested dependencies. Use high risk for any deletion, schema contract change, semantic model or report breaking change, identity or connection change, RLS or OLS change, capacity impact, refresh impact, or production action.

Treat high risk as requiring a written recovery plan and named approval.

## Plan the change

Start from ../../templates/change-plan.md. Include:

1. Target workspace, branch, and commit.
2. Items and dependencies affected.
3. Data classification and whether external model review is permitted.
4. Deterministic validation, smoke checks, and parity checks.
5. Stop conditions, required Azure DevOps checks, and recovery steps.

Prefer a small, reviewable pull request. Keep environment-specific IDs and credentials outside source control.

## Hand off

Save the sanitized plan in the run output folder described by ../../AGENTS.md. Route release work to ../ado-fabric-release/SKILL.md and review work to ../ai-release-review/SKILL.md only after the plan is complete.
