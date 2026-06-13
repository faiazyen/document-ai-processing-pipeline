# SLO And Reliability Notes

This project defines platform-style SLOs and the metrics needed to evaluate them. It does not claim measured production availability until the system is operated under real traffic with external monitoring.

## Target SLOs

| Area | Target | Measurement |
| --- | --- | --- |
| API availability | 99.95% successful non-5xx responses over 30 days | HTTP status metrics |
| Job completion | 99% of valid text-based invoice jobs complete without internal failure | Job status metrics |
| Job latency | 95% of text-based PDFs under 5 MB complete under 30 seconds | `p95_processing_ms` / histogram equivalent |
| Model fallback | OpenAI failures degrade to fallback extraction without API crash | fallback rate and error counters |

99.95% availability allows about 21.6 minutes of downtime per 30-day window.

## Current Instrumentation

- `/health` reports service status, OpenAI configuration, and database kind.
- `/metrics` reports processed documents, failed documents, average processing time, p95 processing time, p95 LLM time, fallback rate, validation warning count, and estimated cost.
- Inference jobs persist status transitions: `queued`, `processing`, `succeeded`, `failed`, `retrying`, and `dead_lettered`.
- Tenant usage aggregates processed jobs, failed jobs, token counts, and estimated cost.

## Production Gap

The current metrics store is in memory. A production deployment should export the same concepts to a durable metrics backend and alert on error budget burn, p95 latency, queue backlog, and failed jobs.
