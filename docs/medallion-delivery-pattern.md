# Medallion delivery pattern

This is a public-safe delivery pattern informed by the supplied architecture plan. It preserves reusable Bronze, Silver, and Gold principles while omitting internal names, capacity figures, source-system details, and operational data.

## Data product flow

~~~mermaid
flowchart LR
  A[Bronze: ingest] --> B[Silver: conform and validate]
  B --> C[Gold: serve and model]
  C --> D[Semantic model and report]
  D --> E[Monitoring and support]
  E --> A
~~~

## Release controls by layer

| Layer | Change focus | Required pre-deploy checks | Required post-deploy checks | Typical stop condition |
| --- | --- | --- | --- | --- |
| Bronze | Ingestion, landing schema, orchestration | Connection policy, schema expectation, parameter review | Freshness, run completion, landing volume threshold | Source or contract unavailable |
| Silver | Transformations, conformance, quality | Schema compatibility, unit or notebook checks, null and duplicate rules | Row-count and quality parity, lineage check | Data-quality threshold breached |
| Gold | Curated model, semantic contract, report binding | Backward compatibility, metric definition, RLS or OLS review | Refresh, semantic smoke test, consumer-impact check | Metric, access, or refresh regression |

## Delivery sequence

1. Plan the affected data layer and contract.
2. Validate the source-controlled artifact and its dependencies.
3. Synchronize the approved Git commit to Dev.
4. Execute bounded layer-specific smoke and parity checks.
5. Attach evidence to the promotion request.
6. Use protected Test and Prod environments for promotion.
7. Feed release failures and data-quality alerts into the sanitized support packet.

## Quality gates

Use explicit thresholds owned by the data product team. Examples include expected freshness window, row-count tolerance, null-rate tolerance, duplicate-rate tolerance, reconciliation total, semantic refresh completion, and authorization behavior. Do not hard-code organization-specific thresholds in this public template.

## Recovery

Prefer an approved prior Git commit or a documented containment action over an ad hoc workspace edit. If the change affects data rather than only metadata, document whether rollback is technically safe before deployment.
