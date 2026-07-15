# Fabric Git release flow

Use this flow when each Fabric workspace is connected to a protected branch. It is based on the Fabric Git integration APIs and follows the pattern Microsoft documents for Git-based Fabric CI/CD.

## Release sequence

1. Merge a reviewed pull request into the environment branch.
2. Run repository validation and create a sanitized release-evidence record.
3. Use the exact workspace ID and expected full commit SHA for that branch.
4. Call Fabric Git status for the workspace.
5. Stop if the returned remote commit does not equal the expected commit or any item has a conflict.
6. Request the protected Azure DevOps environment. Let its checks and approvals decide whether the deployment job starts.
7. Call Update From Git with the status workspace head and remote commit. Permit incoming-item override only as the explicit source-of-truth decision for the release.
8. Poll the long-running operation until it reaches a terminal state.
9. Verify the expected commit, item health, and change-specific smoke or parity checks.
10. Publish sanitized evidence and either promote or create a support incident.

## Why status is required

Fabric Git status returns the workspace head, remote commit hash, changed items, and conflicts. Using those values prevents a pipeline from deploying a commit other than the commit it validated. The status endpoint must not be called while an Update From Git operation is still running.

## API behavior

The Update From Git endpoint is:

~~~text
POST https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/git/updateFromGit
~~~

It requires a remote full commit SHA and normally requires the current workspace head. It can return an accepted response for a long-running operation. Record the returned operation location or operation ID; poll it rather than starting another sync.

The included PowerShell helper follows this API path:

~~~text
scripts/sync-fabric-from-git.ps1
~~~

It runs in planning mode unless the caller supplies explicit execution and incoming-override switches.

## Conflict policy

Do not conceal a conflict by defaulting to workspace or remote content. Reconcile the source of truth, update the change plan, and create an auditable approval before an override. A conflict may mean that someone changed the workspace outside the branch, that an earlier operation did not finish, or that the wrong workspace is targeted.

## Item-specific verification

Add checks according to the actual artifacts:

| Item type | Minimum verification |
| --- | --- |
| Lakehouse or warehouse | Schema compatibility, table availability, data-quality or parity threshold |
| Notebook or Spark job | Compile or lint, parameter validation, bounded smoke run |
| Data Factory pipeline | Dependency validation, connection policy, test-trigger result |
| Semantic model | Refresh result, model schema impact, RLS and OLS review where used |
| Report | Binding and visual smoke check, consumer-impact review |

Do not make unsupported assumptions about item support or service-principal behavior. Confirm the organization’s Fabric item types and current platform support before enabling a real pipeline.
