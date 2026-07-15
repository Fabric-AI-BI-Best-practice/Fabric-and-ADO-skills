# Support packet contract

An incident packet must be useful to an on-call engineer without broadening access to sensitive data.

## Required fields

- Incident ID, severity, reporter time, and owner.
- Impact statement: affected environment, workspace, item type, and user impact.
- Correlation IDs or pipeline run IDs, when available.
- Sanitized symptom, first-seen time, and current status.
- Links to authorized logs and runbooks instead of copied sensitive payloads.
- Recommended containment, escalation, and next evidence to collect.

Use [templates/support-incident.md](../templates/support-incident.md) and create machine-readable output with [scripts/create_support_packet.py](../scripts/create_support_packet.py).
