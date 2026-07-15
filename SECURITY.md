# Security policy

## Reporting

Do not open a public issue for a suspected credential exposure, tenant access issue, or unsafe deployment path. Contact the repository maintainers privately through the contact method configured in the repository settings.

## Safe defaults

- Store credentials in an Azure DevOps service connection, Azure Key Vault, or another approved secret store; never in this repository.
- Use least-privileged identities and distinct Dev/Test/Prod scopes.
- Keep production approvals and checks on Azure DevOps resources. YAML changes alone must not weaken them.
- Redact support logs and release evidence before sharing with people or models outside the authorized boundary.
- Rotate any secret accidentally committed to source control immediately; removing it from Git history does not make it safe.
