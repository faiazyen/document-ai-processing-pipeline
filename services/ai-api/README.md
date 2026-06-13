# Document AI Processing Pipeline — Python FastAPI Backend

This service is the Python backend for the Document AI Processing Pipeline. It exposes a tenant-aware REST API for PDF invoice processing: text extraction, OpenAI structured extraction, rule-based fallback, deterministic validation, async inference jobs, SQLite persistence, usage accounting, and in-memory latency/cost metrics.

## Stack

- Python 3.9+
- FastAPI + uvicorn
- OpenAI Python SDK
- pypdf (text extraction)
- SQLAlchemy + SQLite
- Pydantic v2
- pytest + anyio

## Quick Start

```bash
cd services/ai-api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then add your OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Swagger UI is available at: http://localhost:8000/docs

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /process-invoice | Legacy single-call upload, extract, validate, persist |
| POST | /inference/jobs | Create an authenticated tenant-scoped async job |
| GET | /inference/jobs | List authenticated tenant jobs |
| GET | /inference/jobs/{job_id} | Get one authenticated tenant job |
| GET | /tenants/me | Read authenticated tenant config |
| GET | /tenants/me/usage | Read tenant usage and estimated cost |
| GET | /invoices | List authenticated tenant invoice summaries |
| GET | /invoices/{id} | Get one authenticated tenant invoice by database ID |
| GET | /health | Service health and configuration status |
| GET | /metrics | In-memory counters, p95 latency samples, and estimated cost |

## Running Tests

```bash
# from services/ai-api/
python -m pytest tests/ -v
```

All 32 tests should pass. Tests cover validation logic, fallback extraction, persistence, tenant isolation, API-key auth, usage aggregation, API health/metrics endpoints, OpenAPI exposure, and consistent error responses.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| OPENAI_API_KEY | (empty) | Required for AI extraction. Fallback is used if missing. |
| OPENAI_MODEL | gpt-4.1-mini | OpenAI model name |
| OPENAI_INPUT_USD_PER_1M_TOKENS | 0 | Optional input-token price for estimated cost/request |
| OPENAI_OUTPUT_USD_PER_1M_TOKENS | 0 | Optional output-token price for estimated cost/request |
| DATABASE_URL | sqlite:////tmp/invoices.db | SQLAlchemy connection string. Use `sqlite:///./invoices.db` for a local project-file database. |
| CORS_ALLOW_ORIGIN_REGEX | `^https://.*\.vercel\.app$` | Optional Vercel preview origin regex |
| PLATFORM_DEV_API_KEY | (empty) | Optional local API key seeded for the default tenant |
| API_KEY_HASH_SECRET | local-development-secret | HMAC secret for API key hashes |
| DEFAULT_TENANT_ID | personal-lab | Seed tenant ID |
| DEFAULT_TENANT_NAME | Personal Lab | Seed tenant display name |
| DEFAULT_REGION | local | Default region metadata for jobs |

## Project Structure

```
app/
  main.py              — FastAPI app, CORS, lifespan
  config.py            — pydantic-settings configuration
  schemas.py           — Pydantic request/response models
  routers/
    invoices.py        — all API route handlers
  services/
    extract_text.py    — PDF text extraction, scanned PDF detection
    openai_extract.py  — OpenAI structured extraction
    fallback_extract.py — regex-based field extraction
    validate_invoice.py — deterministic validation rules
    auth.py            — API key hashing and tenant resolution
    costing.py         — token and cost estimation helpers
    persistence.py     — SQLAlchemy CRUD for tenants, jobs, invoices
    pipeline.py        — shared invoice-processing service
    metrics.py         — thread-safe in-memory latency/cost counters
  experimental/
    langchain_extractor.py — optional LangChain alternative (see notes)
tests/
  test_validation.py
  test_fallback_extract.py
  test_health.py
  test_persistence.py
```

## Production Notes

SQLite is used for local experimentation. Replace it with PostgreSQL by changing `DATABASE_URL`; `psycopg` is included for PostgreSQL deployments.

If `OPENAI_API_KEY` is missing or OpenAI fails, the API degrades gracefully to rule-based fallback extraction instead of crashing.

Authenticated platform endpoints require `X-API-Key`. The key is never stored directly; only an HMAC hash is persisted. Set `PLATFORM_DEV_API_KEY` locally to seed a default tenant key at startup.

Scanned PDFs with no extractable text return a `scanned_pdf_requires_ocr` validation warning. A production workflow would route these files to a managed OCR service.
