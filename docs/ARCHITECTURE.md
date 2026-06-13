# Architecture

## System Goal

The app behaves like a small invoice-processing system: parse a document, extract fields with an AI model, distrust the model enough to validate it, and return an explainable result.

The repository has two execution surfaces:

- **Next.js frontend/API route** for the hosted dashboard and Vercel deployment.
- **Python FastAPI backend** for Swagger/OpenAPI, tenant-aware access, async job records, persistence, Docker Compose, health checks, p95 latency metrics, and estimated cost tracking.

## Runtime Flow

```text
Client upload UI
  -> POST /api/process-invoice
  -> PDF validation and text extraction
  -> OpenAI structured extraction
  -> rule-based fallback extraction
  -> fallback merge when critical values are missing or confidence is low
  -> deterministic validation
  -> JSON response rendered by the dashboard
```

## Platform API Flow

```text
API client
  -> X-API-Key tenant resolution
  -> POST /inference/jobs
  -> persisted job: queued
  -> background worker execution: processing
  -> PDF text extraction
  -> OpenAI extraction when configured
  -> fallback extraction and deterministic validation
  -> persisted invoice result and tenant usage
  -> job status: succeeded or failed
```

## Layering

- `src/app`: Next.js routes and server/client composition.
- `src/components`: UI-only rendering and upload state.
- `src/lib/extractText.ts`: PDF validation, parsing, and text normalization.
- `src/lib/openai.ts`: lazy OpenAI client and structured response parsing.
- `src/lib/fallbackExtractor.ts`: regex extraction for critical invoice fields.
- `src/lib/validateInvoice.ts`: deterministic warning engine.
- `src/lib/schemas.ts`: Zod schemas and shared TypeScript types.

## Reliability Strategy

AI output is treated as a candidate extraction, not truth. The app runs deterministic validation every time. If OpenAI is unavailable, malformed, low-confidence, or missing critical fields, the fallback extractor fills the most important values and the response clearly marks the extraction source.

The FastAPI surface also persists job state and tenant usage so API clients can poll for results instead of relying only on synchronous request/response processing.

## Security And Secrets

`OPENAI_API_KEY` is read only from server-side environment variables. No secret is exposed to client components. `.env*` files are ignored, while `.env.example` documents required configuration.

Platform endpoints require `X-API-Key`. API keys are HMAC-hashed before storage; tenant lookups compare hashes rather than raw keys. Tenant-scoped queries prevent one tenant from reading another tenant's jobs or invoices.

## Vercel Readiness

The Next.js app deploys to Vercel. The API route uses the Node.js runtime because PDF parsing runs server-side. `vercel.json` declares the Next.js framework and build/install commands. Production deployment requires setting `OPENAI_API_KEY` in Vercel environment variables.

The Python FastAPI backend is containerized separately. For production, deploy it to a managed container platform or a Vercel-compatible external API host, then point the frontend or integrations at that backend URL.

## Future Production Extensions

- OCR for scanned image-only PDFs.
- Object storage for uploaded documents and outputs.
- Durable queue and independent worker deployment.
- Human review queue for high-severity warnings.
- OpenTelemetry traces around extraction stages.
- Drift monitoring for field-level extraction quality.
- Dataset-backed regression tests from real invoice fixtures.
