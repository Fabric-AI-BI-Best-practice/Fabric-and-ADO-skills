# Real-tenant onboarding

Complete this checklist before copying the pipeline templates into a production Fabric solution.

## Decisions to record

1. Fabric artifacts in scope: lakehouse, warehouse, notebooks, Data Factory pipelines, semantic models, reports, Eventhouse, or other supported types.
2. Exact Dev, Test, and Prod workspace IDs and their connected branches.
3. Azure DevOps organization, project, repository, and named protected environments.
4. Identity model: service principal, managed identity, or approved workload identity federation.
5. Minimum Fabric and Git permissions for each environment.
6. Approved secret store and token-acquisition pattern.
7. Smoke tests, parity thresholds, service-level objectives, and recovery owner.
8. Support intake and telemetry destinations.
9. Data classification permitted in release evidence and external model prompts.
10. Exact model providers and IDs behind any labels such as Claude Code, Fable 5, or Sol 5.6.

## Bring-up order

1. Set up a non-production workspace and a low-risk sample artifact.
2. Connect that workspace to the intended Dev branch through the Fabric UI or the approved setup process.
3. Create the Dev Azure DevOps environment and restricted service connection.
4. Run validation-only YAML on a pull request.
5. Run the Git-sync helper without execution and inspect evidence.
6. Run Dev synchronization with a disposable test change.
7. Add test workspace, protected environment, approvals, and verification.
8. Repeat for Prod only after a recovery exercise and security review.

## Do not onboard until

- The workspace/branch mapping is documented.
- Approval and lock checks work as intended.
- The identity has verified least privilege.
- A failed sync and a verification failure have both been exercised.
- Evidence has been inspected for secret and data leakage.
