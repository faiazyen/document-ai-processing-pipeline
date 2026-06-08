# Document AI Processing Pipeline — Python FastAPI Backend

This service is the Python backend for the Document AI Processing Pipeline. It exposes a REST API for PDF invoice processing: text extraction, OpenAI structured extraction, rule-based fallback, deterministic validation, SQLite persistence, and in-memory metrics.

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
| POST | /process-invoice | Upload PDF, extract, validate, persist |
| GET | /invoices | List all processed invoice summaries |
| GET | /invoices/{id} | Get one invoice by database ID |
| GET | /health | Service health and configuration status |
| GET | /metrics | In-memory counters for monitoring |

## Running Tests

```bash
# from services/ai-api/
python -m pytest tests/ -v
```

All 27 tests should pass. Tests cover validation logic, fallback extraction, persistence (in-memory SQLite), API health/metrics endpoints, OpenAPI exposure, and consistent error responses.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| OPENAI_API_KEY | (empty) | Required for AI extraction. Fallback is used if missing. |
| OPENAI_MODEL | gpt-4.1-mini | OpenAI model name |
| DATABASE_URL | sqlite:///./invoices.db | SQLAlchemy connection string |
| CORS_ALLOW_ORIGIN_REGEX | `^https://.*\.vercel\.app$` | Optional Vercel preview origin regex |

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
    persistence.py     — SQLAlchemy CRUD for invoice records
    metrics.py         — thread-safe in-memory counters
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

Scanned PDFs with no extractable text return a `scanned_pdf_requires_ocr` validation warning. A production workflow would route these files to a managed OCR service.
