# Environment contract

Each deployed environment needs an explicit, approved record. Keep real values in protected Azure DevOps variables or a configuration store, not in this public repository.

## Required fields

| Field | Requirement |
| --- | --- |
| Environment name | One of the organization-approved names, for example dev, test, or prod |
| Fabric workspace ID | UUID for the exact target workspace |
| Connected branch | Full branch ref that Fabric is connected to |
| Azure DevOps environment | Protected Azure DevOps resource used by the deployment job |
| Identity | Named service connection or workload identity with least privilege |
| Data classification | Highest classification that may appear in logs or model inputs |
| Approval policy | Required human approvers and resource checks |
| Recovery owner | Person or group accountable for a failed release |

## Example

~~~json
{
  "environment": "test",
  "fabricWorkspaceId": "<workspace-guid>",
  "connectedBranch": "refs/heads/test",
  "azureDevOpsEnvironment": "fabric-test",
  "identity": "fabric-release-test",
  "dataClassificationForEvidence": "internal-sanitized",
  "requiresHumanApproval": true,
  "recoveryOwner": "data-platform-on-call"
}
~~~

## Guardrails

- Do not point two protected environments at the same workspace.
- Do not let a mutable pipeline variable choose a protected service connection.
- Require the expected branch commit to match Fabric Git status before synchronizing.
- Treat the Fabric workspace as a deployment target, not the primary source of truth.
