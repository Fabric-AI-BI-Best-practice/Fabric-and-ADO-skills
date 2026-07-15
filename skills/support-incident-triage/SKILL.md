---
name: support-incident-triage
description: Triage Microsoft Fabric and Azure DevOps support incidents safely and create auditable incident packets. Use for failed Fabric releases, pipeline failures, workspace Git-sync errors, refresh issues, broken data contracts, degraded reports, support intake, on-call handoffs, or post-incident evidence collection.
---

# Fabric support incident triage

Create a useful incident packet without exposing sensitive data.

## First response

1. Record the incident ID, severity, time, owner, affected environment, workspace, item type, and user impact.
2. Decide whether to contain, investigate, or escalate immediately.
3. Preserve relevant pipeline run IDs, Fabric operation IDs, and correlation IDs.
4. Redact data values, tokens, connection strings, personal data, and customer identifiers before sharing evidence.

Read ../../common/support-packet-contract.md and use ../../templates/support-incident.md.

## Severity guide

- Sev 1: production outage, security concern, or broad business stoppage. Escalate immediately and avoid unapproved remediation.
- Sev 2: major degraded capability or failed protected release. Contain and involve the service owner.
- Sev 3: limited impact with a documented workaround. Create a bounded plan and evidence packet.
- Sev 4: question, cosmetic issue, or non-urgent improvement. Route to backlog with enough context to reproduce.

## Automated packet

Use ../../scripts/create_support_packet.py to create a machine-readable skeleton. Attach links to approved log locations rather than copying raw logs. Use ../ai-release-review/SKILL.md only on sanitized packets and only for advisory analysis.

## Closeout

Record root cause, containment, fix, validation, follow-up owner, and prevention action. Do not silently close a release incident because a retry succeeded.
