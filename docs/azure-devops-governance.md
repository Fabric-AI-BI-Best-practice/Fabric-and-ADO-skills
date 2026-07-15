# Azure DevOps governance

Azure DevOps resource checks are the authorization boundary for protected deployments. Keep them outside version-controlled YAML so a pull request cannot weaken them.

## Configure once per protected environment

For fabric-test and fabric-prod, configure:

1. Manual approval with named groups and no self-approval if policy requires it.
2. Branch control allowing only the intended protected branch.
3. Exclusive lock to avoid concurrent updates to the same workspace.
4. Optional business-hours, Azure Monitor, REST, or change-management checks where the organization uses them.
5. A restricted service connection with a required template check when appropriate.

## Pipeline responsibility

The YAML template should:

- validate source artifacts before deployment;
- target the named Azure DevOps environment through a deployment job;
- obtain a short-lived Fabric token through the approved identity;
- pass the exact Build.SourceVersion to Fabric Git sync;
- publish sanitized evidence;
- fail closed when a status check, approval, sync, or verification fails.

## What must remain outside YAML

- Approval group membership.
- Environment and service-connection permissions.
- Secret values and Key Vault access.
- Branch policies.
- Emergency bypass authorization.

## Release history

Link every production deployment to its pipeline run, change plan, release evidence, and support incident if one exists. Preserve the record even if the release is rolled back.
