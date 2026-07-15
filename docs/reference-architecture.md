# Reference architecture

This architecture uses Git as the source of truth for Fabric item definitions and Azure DevOps as the controlled orchestration layer.

~~~mermaid
sequenceDiagram
  participant Dev as Developer
  participant Git as Azure Repos
  participant ADO as Azure Pipelines
  participant Gate as Protected ADO Environment
  participant Fabric as Fabric Workspace
  participant Support as Support Queue

  Dev->>Git: Pull request
  Git->>ADO: Trigger validation
  ADO->>ADO: Validate artifacts and build evidence
  ADO->>Gate: Request environment checks
  Gate-->>ADO: Approval and branch checks pass
  ADO->>Fabric: Get Git status and update from Git
  Fabric-->>ADO: Long-running operation result
  ADO->>Fabric: Smoke and parity verification
  ADO->>Support: Attach sanitized evidence on failure
~~~

## Components

| Component | Responsibility | Must not do |
| --- | --- | --- |
| Source repository | Version Fabric item definitions, YAML, validation code, and policy | Store credentials or customer data |
| Pull request | Review change scope and run deterministic checks | Directly update a protected workspace |
| Azure DevOps environment | Enforce branch control, approvals, locks, and audit trail | Be selected by an untrusted mutable variable |
| Fabric workspace | Host the corresponding environment and synchronize approved Git state | Be the only record of a release |
| Evidence package | Preserve sanitized proof of decision and outcome | Contain raw logs or secrets |
| AI reviewers | Find policy gaps, missing tests, or risk | Deploy, approve, or override a failed control |
| Support queue | Route incidents and capture recovery learning | Become a raw-log data lake |

## Recommended branch and workspace mapping

| Git branch | Fabric workspace | Azure DevOps environment | Promotion |
| --- | --- | --- | --- |
| feature slash | Isolated feature workspace or local validation | None | Pull request to Dev |
| dev | Shared Dev workspace | fabric-dev | Automatic only after PR validation |
| test | Test workspace | fabric-test | Protected approval |
| main | Production workspace | fabric-prod | Protected approval, lock, and post-deploy verification |

The mapping is an example, not a universal requirement. Record the actual mapping in protected environment configuration.

## Trust boundaries

1. Git changes are untrusted until PR policy and validation succeed.
2. YAML may request a deployment but cannot replace Azure DevOps resource checks.
3. A deployment identity has only the permissions required for its environment.
4. Fabric Git sync accepts only the expected remote commit and a clean conflict state.
5. Model analysis is outside the release authority boundary and receives sanitized evidence only.

## Failure design

If a sync is blocked, preserve evidence, stop promotion, and inspect workspace Git status. If a sync succeeds but verification fails, contain the affected environment, create a support packet, and select recovery through the approved owner. Do not automatically reverse data-changing operations without an explicit recovery plan.
