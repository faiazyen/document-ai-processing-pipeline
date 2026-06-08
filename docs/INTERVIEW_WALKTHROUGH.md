# Interview Walkthrough

## 60-Second Summary

This is a document AI pipeline for B2B merchandise invoices. It extracts PDF text, calls OpenAI for structured invoice extraction, falls back to deterministic regex extraction when the model is unavailable or incomplete, validates financial consistency across 10+ rules, persists every result to an audit log, and returns explainable JSON with confidence scores and warnings.

The system has two implementations: a **Next.js TypeScript frontend** (Vercel-deployable) and a **Python FastAPI backend** (Docker/Kubernetes-ready), both using identical logic and the same invoice schema.

---

## Problem

B2B merchandise suppliers send invoices in hundreds of different formats. Manual data entry is slow, error-prone, and doesn't scale. A document AI pipeline needs to:

1. Extract structured fields reliably even when the LLM returns incomplete data.
2. Validate numeric consistency (tax totals, subtotals) independently of extraction.
3. Degrade gracefully when OpenAI is unavailable — never crash the golden path.
4. Log every result for audit, debugging, and quality monitoring.

---

## Architecture

```
PDF upload
  → text extraction (pdf-parse / pypdf)
  → scanned PDF detection → OCR warning if image-only
  → OpenAI structured extraction (gpt-4.1-mini, JSON mode)
  → rule-based fallback when confidence < 0.74 or critical fields missing
  → deterministic validation (10+ rules, three severity levels)
  → SQLite persistence / audit log (PostgreSQL-ready)
  → JSON response to dashboard
```

The system runs this pipeline twice: once in TypeScript (Next.js) and once in Python (FastAPI). The Python backend is the production-style service; the TypeScript API route demonstrates that the same logic can be embedded in a Next.js app for Vercel deployment.

---

## Why Invoices

B2B merchandise (custom apparel, uniforms, branded goods) involves high-volume, multi-line invoices from suppliers across different countries. Fields like currency, VAT rate, and payment terms vary significantly. This makes invoices harder than simple structured forms — they need AI extraction plus rule-based validation to be reliable.

---

## Why OpenAI + Fallback Validation

**OpenAI** gives good baseline coverage on text-based PDFs with minimal code. Structured JSON output mode (previously called "function calling") constrains the response to a known schema.

**Fallback** is necessary because:
- API keys expire.
- Rate limits happen.
- OpenAI sometimes returns partial results or low-confidence extractions.
- The demo must work without billing the interviewer.

**Deterministic validation** is first-class because:
- You cannot trust model output alone on financial data.
- Rules like "total ≥ subtotal" and "subtotal + VAT = total (±0.02)" are not statistical — they are accounting facts.
- Warnings with severity levels give the human reviewer actionable triage criteria.

---

## Why FastAPI Backend

The Python FastAPI service was added to demonstrate the full GenAI/AI Platform Engineer skill set:

- **Python** — all backend code in Python 3.9+
- **FastAPI** — async REST API with auto-generated OpenAPI 3.1 spec
- **Swagger/OpenAPI** — interactive docs at `/docs`, contract-first design
- **SQLAlchemy + SQLite** — ORM-based persistence with a clear path to PostgreSQL
- **pytest + anyio** — async test suite covering 24 test cases
- **Docker + Docker Compose** — containerized local development and deployment
- **Kubernetes** — reference manifests with HPA, health probes, and resource limits

---

## How Swagger / OpenAPI Works

FastAPI generates a `/openapi.json` spec automatically from type annotations and Pydantic models. This spec powers:
- Swagger UI at `/docs` — interactive endpoint testing
- ReDoc at `/redoc` — readable documentation
- Auto-generated client SDKs via `openapi-generator`
- API gateway integration (AWS API Gateway, Kong, Azure APIM)

This means the schema is always in sync with the implementation — no separate documentation maintenance.

---

## How Persistence / Audit Logs Work

Every processed invoice is saved to SQLite via SQLAlchemy ORM:
- Input filename, output JSON, validation warnings (serialized), extraction source, confidence score, processing time.
- `GET /invoices` returns all records for dashboard display.
- `GET /invoices/{id}` retrieves a specific result by database ID.

The persistence layer is wrapped in `try/except` — a database failure never crashes the API response. The extraction result is still returned with `id: -1` to signal the save failed.

SQLite is used in the demo; changing `DATABASE_URL` to a PostgreSQL connection string is the only change needed for production.

---

## How Docker / CI/CD Support Production Thinking

**Docker Compose** brings up both services with a single command. The backend health check gates the frontend startup, so services come up in the right order.

**GitHub Actions CI** runs two parallel jobs:
- `frontend` — ESLint, 5 Vitest tests, production Next.js build
- `backend` — 24 pytest tests with `OPENAI_API_KEY=""` (no API call in CI)

This demonstrates: no secrets in CI, all tests pass without external dependencies, and both stacks are validated on every push.

---

## Limitations

| Limitation | Why It Exists | Production Fix |
|-----------|---------------|----------------|
| SQLite is single-writer | Portfolio demo simplicity | PostgreSQL/Supabase via `DATABASE_URL` |
| No OCR for scanned PDFs | Keep demo stable | AWS Textract / Azure Document Intelligence |
| No auth on endpoints | Open demo | FastAPI `HTTPBearer` or OAuth2 |
| Metrics reset on restart | In-memory counters | Prometheus + Grafana |
| Synchronous PDF processing | No queue infrastructure | Celery + Redis or AWS SQS |

---

## Future Improvements

1. Scanned PDF OCR via Textract or Tesseract.
2. Field-level confidence scores (per-field, not document-level).
3. Labeled fixture corpus for dataset evaluation and regression testing.
4. Human review UI for invoices with high-severity warnings.
5. LangChain multi-step chain: extract → validate → summarize → route.
6. OpenTelemetry traces around each extraction stage.
7. Kubernetes HPA for bursty load handling (manifests in `k8s/`).

---

## Rossum-Relevant Framing

Rossum-style systems need extraction quality, explainability, and operational reliability. This project shows the same mindset:

- Model output is validated deterministically — AI is a candidate, not truth.
- Missing fields and arithmetic errors are surfaced with severity levels.
- Fallback extraction makes the demo resilient without pretending regex is enough.
- Audit logs preserve every processing decision.
- Production-readiness gaps are documented honestly, with clear upgrade paths.
- The Python FastAPI backend directly mirrors the kind of document processing microservice Rossum would build internally.
