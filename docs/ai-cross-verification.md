# AI cross-verification

Use two independent model roles to improve review coverage, not to automate approval.

## Configure before use

For every reviewer profile, record:

- Provider and exact model identifier.
- How the model is accessed and who may invoke it.
- Data-retention, training, regional, and audit terms.
- Maximum data classification permitted in prompts.
- Rate, cost, and timeout limits.
- Named owner for the model integration.

Do not treat a familiar product label as a model identifier. Claude Code, Fable 5, and Sol 5.6 are placeholders until this record exists.

## Review packet

Start with [review request example](../templates/ai-review/request.example.json). Include a frozen commit, target, risk assessment, affected artifact metadata, deterministic test results, approval policy, recovery plan, and precise review questions.

For high-risk semantic-model changes, explicitly include backward-compatibility impact, report dependencies, measure or relationship changes, RLS and OLS impact, refresh and capacity evidence, and rollback rehearsal evidence.

## Independent process

1. Give identical sanitized evidence to Reviewer A and Reviewer B.
2. Change only the reviewer role and keep the reviewers blind to each other's result.
3. Require each to return [the review response schema](../templates/ai-review/review-response.schema.json).
4. Compare findings with deterministic evidence and policy.
5. Escalate if either review identifies a blocker, if the reviewers materially disagree, or if evidence is incomplete.
6. Have a named human record the disposition of each material finding.
7. Let the protected Azure DevOps environment, not the models, control deployment.

## Evidence retention

Save only sanitized request and response files with the release evidence. Keep any provider-specific transcripts or service logs in the approved system of record and subject to its retention policy.
