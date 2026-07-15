---
name: ado-fabric-release
description: Build or operate governed Azure DevOps pipelines that validate and promote Microsoft Fabric changes. Use when a user asks to create, review, run, or troubleshoot Azure Pipelines for Fabric CI/CD, branch progression, deployment approvals, service connections, release evidence, or rollback controls.
---

# Azure DevOps Fabric release

Use Azure DevOps to orchestrate a controlled Fabric release, not to bypass Fabric or environment governance.

## Release design

Read ../../common/environment-contract.md, ../../common/release-evidence-contract.md, and ../../docs/fabric-git-release-flow.md.

Separate validation from deployment:

1. Validate pull requests and artifacts before merge.
2. Synchronize Dev only from the approved Dev branch.
3. Promote through protected Test and Prod environments.
4. Verify after each target update.

Use a deployment job that targets a named Azure DevOps environment. Configure approvals, branch control, exclusive locks, required templates, and service-connection checks on the protected resource outside YAML.

## Identity and secrets

Use an approved Entra-backed service connection or managed identity. Obtain short-lived Fabric access tokens during the job where possible. Keep service-connection references explicit and protected. Never place a token, secret, client credential, or connection string in YAML, evidence, pull requests, or model prompts.

## Pipeline execution

Start with the templates in ../../templates/azure-pipelines. Before a run:

1. Confirm the branch is allowed for the target.
2. Confirm the variable group identifies one workspace only.
3. Run repository validation and unit tests.
4. Build a release-evidence record.
5. Require Azure DevOps resource checks.
6. Use ../fabric-git-sync/SKILL.md for the actual workspace update.
7. Publish only sanitized evidence.

## Failure behavior

Do not retry an unknown or timed-out Fabric operation blindly. First inspect the operation and workspace Git status. Preserve the failed evidence, contain the impact, and follow the recovery plan.
