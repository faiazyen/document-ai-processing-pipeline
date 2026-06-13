# Platform Capabilities

## Implemented

- Tenant records with status, preferred model, region preference, and optional usage limits.
- HMAC-hashed API keys for FastAPI platform endpoints.
- Tenant-scoped invoice and job reads.
- Async inference job API using FastAPI background execution.
- Persisted job state, request ID, region metadata, raw text preview, extraction result, latency fields, token counts, and estimated cost.
- Deterministic validation and fallback extraction around OpenAI output.
- In-memory p95 latency and estimated cost metrics.
- Docker Compose and Kubernetes reference manifests with HPA configuration for the backend service.

## Not Yet Production-Grade

- Background execution is local to the API process; a durable external queue is still needed for crash-safe execution.
- Metrics are in-memory; production needs a metrics backend and dashboards.
- Region support is metadata/design-level; there is no active multi-region routing layer.
- 99.95% SLOs are defined but not measured from live production history.

## Truthful Summary

The project is now a tenant-aware document inference platform prototype with async job processing, cost and latency instrumentation, tenant isolation, and deployment-ready infrastructure references.
