# Fabric and ADO Skills

An independent, public-safe starter kit for governing Microsoft Fabric changes with Azure DevOps. It combines small agent skills, deterministic validation, evidence-based review, and human-controlled promotion.

> This is a community project. It is not affiliated with, endorsed by, or supported by Microsoft. It contains no tenant IDs, credentials, customer data, or production automation defaults.

## The operating model

~~~mermaid
flowchart LR
  A["1. Change<br/>Feature branch and pull request"] --> B["2. Validate<br/>Artifacts, secrets, and tests"]
  B --> C["3. Review<br/>Sanitized release evidence and human decision"]
  C --> D["4. Sync Dev<br/>Fabric Git sync, smoke, and parity"]
  D --> E{"5. Promote<br/>Test / Prod approval"}
  E --> F["6. Operate<br/>Workspace sync, monitoring, and triage"]

  K["Independent AI review<br/>(advisory)"] -. Findings .-> C
~~~

Deterministic checks and Azure DevOps resource approvals decide whether a release may proceed. The dashed AI input is advisory: it can identify risks and draft recommendations, but it never receives deployment authority. A failed check, declined approval, or Fabric conflict stops promotion and returns the work to a new pull request.

## What is included

- Six focused skills for Fabric planning, Git synchronization, Azure DevOps releases, verification, support triage, and cross-model review.
- Azure Pipelines examples for PR validation plus Dev, Test, and Prod synchronization.
- A safe PowerShell Fabric Git-sync helper that reads workspace status, rejects conflicts, asserts the expected commit, invokes the supported Fabric API only with explicit execution flags, and polls the long-running operation.
- Release-evidence and support-packet contracts, examples, and dependency-free validation scripts.
- Public-safe governance guidance and upstream attribution.
- A cross-verification packet and reviewer profile pattern for Claude Code, Fable 5, Sol 5.6, or another approved model.

## Quick start

1. Read [AGENTS.md](AGENTS.md), then choose the relevant skill in [skills](skills).
2. Adopt the branch progression feature slash -> dev -> test -> main. Map each long-lived branch to a separate Fabric workspace.
3. Create Azure DevOps environments named fabric-dev, fabric-test, and fabric-prod. Configure approvals, branch controls, and exclusive locks outside YAML.
4. Create an Azure DevOps variable group per environment for non-secret configuration such as FABRIC_WORKSPACE_ID. Configure an Entra-backed service connection separately; never add a credential to this repository.
5. Copy the YAML files in [templates/azure-pipelines](templates/azure-pipelines) into the target Fabric solution repository, replace the intentionally obvious service-connection placeholder, and register each pipeline in Azure DevOps.
6. Run the validation pipeline on a pull request. Use the Dev/Test/Prod sync pipelines only after the matching Fabric workspace is connected to the corresponding branch.

For a real tenant, read [environment contract](common/environment-contract.md) and [Fabric Git release flow](docs/fabric-git-release-flow.md) before enabling execution.

## Safety boundaries

- Never put tokens, passwords, connection strings, customer data, or unredacted logs in Git, evidence packages, or model prompts.
- Never infer a production workspace, branch, or approval. Stop if the target is ambiguous.
- Never auto-resolve a Fabric conflict. Reconcile it through a pull request or an explicitly approved recovery run.
- Require an Azure DevOps environment approval for Test and Prod. Use protected resource checks, not a YAML-only condition.
- Treat output from Claude Code, Fable 5, Sol 5.6, or any other model as advisory until a human and deterministic checks approve the release.

## Repository map

| Path | Purpose |
| --- | --- |
| [skills](skills) | Compact, tool-agnostic operating instructions for agents |
| [common](common) | Canonical contracts and governance rules |
| [templates](templates) | Pipeline, evidence, review, and work-item templates |
| [scripts](scripts) | Dependency-free validation and opt-in Fabric sync helpers |
| [docs](docs) | Architecture, release flow, support operating model, references |
| [examples](examples) | Sanitized example evidence and review packets |

## v1 scope and next decision

This first version is deliberately tenant-agnostic. It demonstrates the supported Git-sync release pattern without connecting to any workspace. To wire it to a real tenant, decide the target item types, Azure DevOps project, Dev/Test/Prod workspace IDs, identity model, approved telemetry source, and allowed data classification for model review. See [real-tenant onboarding](docs/real-tenant-onboarding.md).

For a reusable Bronze, Silver, and Gold delivery view derived from the supplied plan without exposing its internal details, see [medallion delivery pattern](docs/medallion-delivery-pattern.md).

For the model-review setup and decision rules, see [AI cross-verification](docs/ai-cross-verification.md).

## Contributing

Use [CONTRIBUTING.md](CONTRIBUTING.md) and keep changes public-safe. When adding a workflow, include a deterministic check, a rollback or recovery path, and a testable evidence output.

## References

Technical design is based on current official documentation and independently written patterns. See [references and attribution](docs/references-and-attribution.md).
