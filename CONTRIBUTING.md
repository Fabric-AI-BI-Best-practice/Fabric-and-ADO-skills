# Contributing

Keep contributions focused, public-safe, and testable.

1. Open a pull request with a clear problem statement, risk level, and validation evidence.
2. Do not include tenant identifiers, secrets, proprietary Fabric artifacts, customer data, or unredacted support logs.
3. For a new deployment pattern, include deterministic validation, failure behavior, and the expected evidence record.
4. For a new skill, keep SKILL.md concise, add accurate trigger metadata, generate agents/openai.yaml, and run the skill validator.
5. For an upstream adaptation, update [references and attribution](docs/references-and-attribution.md) and retain required license notices.

Maintainers may reject a change that makes production automation implicit, makes AI a release authority, or cannot be safely tested without a tenant.
