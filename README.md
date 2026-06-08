# Document AI Processing Pipeline

[![CI](https://github.com/faiazyen/document-ai-processing-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/faiazyen/document-ai-processing-pipeline/actions/workflows/ci.yml)

A personal document-processing experiment for extracting structured invoice data from PDF files. The project combines a Next.js dashboard, a Python FastAPI service, deterministic validation, fallback extraction, persistence, tests, Docker, and deployment-ready configuration.

The goal is simple: take an invoice PDF, extract useful text, ask an LLM for structured fields, verify the result with deterministic rules, and show the final JSON in a way that is easy to inspect.

---

## Architecture

```mermaid
graph TD
    A[PDF Upload] --> B[Text Extraction]
    B --> C{Readable Text?}
    C -- No --> D[OCR Warning]
    C -- Yes --> E[Structured LLM Extraction]
    E --> F{Low Confidence or Missing Fields?}
    F -- Yes --> G[Rule-Based Fallback Merge]
    F -- No --> H[Use Structured Result]
    G --> I[Deterministic Validation]
    H --> I
    I --> J[Persist Result]
    J --> K[JSON Response + Dashboard]
```

The repository includes two ways to run the pipeline:

- **Next.js app**: interactive dashboard and API route for PDF uploads.
- **FastAPI service**: standalone REST API with Swagger/OpenAPI, persistence, health checks, and metrics.

---

## Stack

### Frontend

- Next.js 16 App Router
- React 19
- TypeScript
- Tailwind CSS v4
- `pdf-parse`
- OpenAI TypeScript SDK
- Vitest

### Backend

- Python 3.11
- FastAPI
- Pydantic v2
- SQLAlchemy
- SQLite for local persistence
- PostgreSQL-compatible database configuration
- `pypdf`
- OpenAI Python SDK
- pytest

### Infrastructure

- Docker
- Docker Compose
- GitHub Actions CI
- Vercel-ready frontend deployment
- Kubernetes reference manifests

---

## What It Does

- Uploads PDF invoices.
- Extracts readable PDF text.
- Detects image-only PDFs that need OCR.
- Produces structured invoice fields.
- Uses fallback rules when structured extraction is incomplete.
- Validates missing fields, currency, totals, tax arithmetic, line items, and confidence.
- Persists processed invoices through the FastAPI service.
- Exposes `/health`, `/metrics`, `/docs`, and `/openapi.json`.
- Renders confidence, warnings, and final JSON in the UI.

---

## Local Frontend Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

Frontend runs at:

```text
http://localhost:3000
```

Add `OPENAI_API_KEY` to `.env.local` only if you want live LLM extraction. Without it, the pipeline still runs with deterministic fallback extraction.

---

## Local FastAPI Setup

```bash
cd services/ai-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

Core endpoints:

| Method | Path | Description |
| --- | --- | --- |
| POST | `/process-invoice` | Upload and process a PDF invoice |
| GET | `/invoices` | List processed invoice summaries |
| GET | `/invoices/{id}` | Read one processed invoice |
| GET | `/health` | Service status |
| GET | `/metrics` | In-memory processing counters |

---

## Docker Compose

```bash
OPENAI_API_KEY=your-key docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- FastAPI + Swagger: http://localhost:8000/docs

Stop everything:

```bash
docker compose down
```

---

## Commands

```bash
# Frontend
npm run dev
npm run lint
npm test
npm run build

# Backend
cd services/ai-api
python -m pytest tests/ -v

# Docker
docker compose build
docker compose up -d
docker compose down
```

---

## Test Coverage

| Suite | Tests |
| --- | ---: |
| TypeScript / Vitest | 11 |
| Python / pytest | 27 |
| Total | 38 |

Tests cover fallback extraction, validation rules, persistence, health/metrics endpoints, OpenAPI exposure, and API error response shape.

---

## Example Output

```json
{
  "document_type": "invoice",
  "supplier_name": "Northstar Print Studio",
  "buyer_name": "Atlas Retail Group",
  "invoice_number": "INV-2026-042",
  "invoice_date": "2026-06-08",
  "due_date": "2026-06-30",
  "currency": "USD",
  "subtotal": 2940,
  "vat_amount": 588,
  "total_amount": 3528,
  "line_items": [
    {
      "description": "Custom Embroidered Hoodies",
      "quantity": 120,
      "unit_price": 24.5,
      "total": 2940
    }
  ],
  "payment_terms": "Net 30",
  "confidence_score": 0.91,
  "validation_warnings": [],
  "extraction_source": "openai"
}
```

---

## Design Notes

This project intentionally keeps AI output behind a validation boundary. The model can help extract structure, but deterministic code decides whether the result is complete, internally consistent, and safe to present.

Known limitations:

- OCR is not implemented yet.
- The fallback extractor is intentionally conservative.
- Metrics are in-memory and reset on restart.
- Authentication and rate limiting are not included.
- Large batch processing would need a queue-based worker design.

Future improvements:

- OCR for scanned documents.
- Field-level confidence.
- Labeled fixture set for extraction-quality regression tests.
- Object storage for uploaded PDFs.
- Authenticated API access.
- Prometheus/OpenTelemetry instrumentation.
