# Support operating model

The support pipeline converts a failed release or reported issue into a small, auditable packet. It should automate consistent intake and routing, not indiscriminately collect production data.

## Automated path

~~~mermaid
flowchart TD
  A[Pipeline failure or support request] --> B[Create packet]
  B --> C[Sanitize identifiers and logs]
  C --> D{Severity}
  D -->|Sev 1 or security| E[Immediate human escalation]
  D -->|Sev 2| F[Contain + service owner]
  D -->|Sev 3 or 4| G[Route to runbook or backlog]
  E --> H[Evidence-linked resolution]
  F --> H
  G --> H
~~~

## Incident packet fields

- Target environment, workspace, item type, and impact.
- Pipeline run and Fabric operation identifiers.
- Sanitized symptom and first-seen time.
- Authorized log links, not copied raw logs.
- Containment action, owner, escalation route, and next evidence.

## Triage authority

Automation may create a ticket, populate the packet, label severity from explicit rules, and recommend an owner. A person decides whether to change data, rerun a production job, roll back, or disclose any evidence outside the authorized boundary.

The included Azure Pipelines template is a safe automation target: it creates and publishes a sanitized packet from explicit run variables. Connect it to a real failure event only after the organization chooses its intake source, event handler, authentication, and redaction policy. Until then, queue it manually or from an approved service-hook handler.

## Model-assisted triage

Use an AI reviewer only after redaction. Ask it to compare the sanitized packet against a runbook and identify missing evidence or likely categories. Keep a human reviewer for severity confirmation and remediation authorization.
