# AI governance for release review

## Allowed model input

- Change summary, diff statistics, file names, allowed metadata, policy text, sanitized validation results, and a redacted evidence package.
- No secrets, customer data, raw workspace exports, unredacted production logs, or personal data.

## Required model output

Each reviewer returns JSON matching [templates/ai-review/review-response.schema.json](../templates/ai-review/review-response.schema.json):

- an independent verdict: approve, revise, or escalate;
- findings tied to evidence or policy;
- a confidence level;
- a recommended human action.

## Separation of duties

- An authoring model may draft a plan, code, or test.
- A reviewer model must receive the policy, the diff, and evidence, not just the author model's conclusion.
- Neither model may invoke deployment, alter approvals, rotate secrets, or override a failed deterministic control.
- Model names are configuration labels. Treat Claude Code, Fable 5, and Sol 5.6 as unverified aliases until the organization records exact provider, model ID, data terms, access method, and retention policy.
