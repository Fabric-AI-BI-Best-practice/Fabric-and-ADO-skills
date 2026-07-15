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
