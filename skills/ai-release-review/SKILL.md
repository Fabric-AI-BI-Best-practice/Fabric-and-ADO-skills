---
name: ai-release-review
description: Perform independent, evidence-based AI review of Microsoft Fabric and Azure DevOps release plans without granting deployment authority. Use when a user asks to cross-check a Fabric change or release with Claude Code, Fable 5, Sol 5.6, another model, or an adversarial reviewer, and when the result must be auditable and safe for human approval.
---

# AI release review

Use models as independent reviewers of sanitized evidence, never as release authorities.

## Prepare the review packet

Read ../../common/ai-governance.md and ../../common/release-evidence-contract.md. Provide only:

1. Change plan and risk level.
2. Sanitized diff summary and affected artifact metadata.
3. Deterministic validation results.
4. Release evidence and stated approval policy.
5. Specific review questions.

Use ../../templates/ai-review/request.example.json. Do not send secrets, data rows, workspace exports, unredacted logs, or credentials.

## Run two independent reviews

Assign distinct author and reviewer roles. Do not let the reviewer see only a prior model verdict. Ask each reviewer to return structured findings with evidence, confidence, and a verdict of approve, revise, or escalate.

Treat Claude Code, Fable 5, and Sol 5.6 as configurable labels until exact providers, model IDs, data-retention terms, and access methods are approved. Do not claim that this repository invokes any external model.

## Resolve findings

1. Compare findings against deterministic evidence and policy.
2. Require a human to decide whether a finding changes the release plan.
3. Record the decision and rationale in the evidence package.
4. Do not use a model verdict to override a failed check, approval, conflict, or production gate.

Return a concise reviewer comparison and an explicit statement that deployment authority remains with the protected Azure DevOps environment and named human approvers.
