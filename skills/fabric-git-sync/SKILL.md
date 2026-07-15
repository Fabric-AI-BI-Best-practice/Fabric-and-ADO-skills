---
name: fabric-git-sync
description: Safely synchronize a Microsoft Fabric workspace from its connected Git branch. Use when a user asks to update a Fabric workspace from Azure DevOps or GitHub, automate Fabric Git integration, inspect Git status, handle a Git-sync conflict, or run a Fabric deployment that uses the Update From Git API.
---

# Fabric Git sync

Synchronize a Fabric workspace only when the source branch, target workspace, identity, and expected commit are explicit.

## Preconditions

Read ../../common/environment-contract.md and ../../docs/fabric-git-release-flow.md. Confirm:

1. The workspace is connected to the intended branch.
2. The caller has the supported Fabric permissions and Git credentials.
3. The expected commit is the full remote commit SHA.
4. The target Azure DevOps environment has completed its required resource checks.

Do not configure a new Git connection or initialize one during a release unless the change plan explicitly authorizes setup work.

## Safe sync sequence

1. Get Fabric Git status.
2. Fail on conflicts, a remote commit mismatch, or an unexpected workspace target.
3. Save sanitized status as release evidence.
4. Run ../../scripts/sync-fabric-from-git.ps1 without execution first.
5. Invoke execution only after validation and the environment gate are satisfied.
6. Poll the Fabric long-running operation and record its operation ID and final state.
7. Hand the result to ../fabric-release-verify/SKILL.md.

## Conflict handling

Do not auto-resolve a conflict. Stop, identify the workspace and remote changes, determine the source of truth through a pull request or approved recovery decision, and rerun the plan. A remote override is an explicit action, never a default.

## Output

Report the workspace ID, branch, expected commit, Git status summary, operation ID, final state, and recovery owner. Do not include access tokens, connection details, raw data, or unredacted logs.
