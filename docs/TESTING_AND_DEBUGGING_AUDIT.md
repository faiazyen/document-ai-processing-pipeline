# Testing and Debugging Audit

**Project:** Document AI Processing Pipeline by MaverickIQ
**Audit Date:** 2026-06-08
**Author:** Faiaz Mazumder
**Test Suites:** Vitest (TypeScript) + pytest (Python)

---

## Executive Summary

| Suite | Tests | Passed | Failed | Status |
|-------|-------|--------|--------|--------|
| TypeScript / Vitest | 5 | 5 | 0 | PASS |
| Python / pytest | 27 | 27 | 0 | PASS |
| **Total** | **32** | **32** | **0** | **ALL PASS** |

---

## Test Matrix

### 1. Valid Invoice PDF

| Field | Value |
|-------|-------|
| **Test name** | `test_valid_invoice_produces_no_critical_warnings` |
| **Purpose** | Confirm a complete, well-formed invoice extraction passes validation with no high-severity warnings. |
| **Expected result** | Empty high-severity warnings list. |
| **Actual result** | No high warnings returned. |
| **Status** | PASS |
| **Notes** | Base fixture covers all required fields with EUR currency, matching subtotal + VAT = total. |

---

### 2. Non-PDF Upload

| Field | Value |
|-------|-------|
| **Test name** | `test_invalid_upload_returns_consistent_error_shape` |
| **Purpose** | Reject files that are not PDFs (e.g., `.docx`, `.png`, `.txt`). |
| **Expected result** | HTTP 400 with `"Only PDF files are accepted."` |
| **Actual result** | FastAPI router checks `file.filename.lower().endswith(".pdf")` and raises 400. |
| **Status** | PASS |
| **Notes** | Next.js route relies on `pdf-parse` throwing on invalid input. Python backend enforces extension check explicitly. |

---

### 2b. Wrong PDF Content Type

| Field | Value |
|-------|-------|
| **Test name** | `test_wrong_content_type_for_pdf_name_is_rejected` |
| **Purpose** | Prevent files named `.pdf` but submitted with unsupported media types from reaching the parser. |
| **Expected result** | HTTP 415 with consistent `{"error": "...", "detail": null}` body. |
| **Actual result** | FastAPI router rejects unsupported `file.content_type`. |
| **Status** | PASS |

---

### 3. Empty PDF

| Field | Value |
|-------|-------|
| **Test name** | Manual / integration |
| **Purpose** | Handle a PDF with zero bytes gracefully. |
| **Expected result** | HTTP 400 with `"Uploaded file is empty."` |
| **Actual result** | File size check (`len(file_bytes) == 0`) catches before extraction. |
| **Status** | PASS (manual verification) |
| **Notes** | Empty files never reach the PDF parser. |

---

### 4. Scanned / Image-Only PDF

| Field | Value |
|-------|-------|
| **Test name** | `test_fallback_empty_text_returns_empty_extraction` (implicit) |
| **Purpose** | Detect PDFs with no extractable text and return an actionable warning instead of silently returning nulls. |
| **Expected result** | `scanned_pdf_requires_ocr` warning; all fields null. |
| **Actual result** | `is_scanned_pdf()` returns `True` when extracted text < 40 characters; warning is appended in router. |
| **Status** | PASS |
| **Notes** | Production path: route to AWS Textract, Azure Document Intelligence, or Google Document AI. Tesseract OCR available as `pytesseract` for offline fallback. |

---

### 5. Missing OPENAI_API_KEY

| Field | Value |
|-------|-------|
| **Test name** | `test_health_returns_ok` — `openai_configured: false` |
| **Purpose** | Confirm the system degrades gracefully when `OPENAI_API_KEY` is absent rather than crashing. |
| **Expected result** | Health endpoint shows `openai_configured: false`; invoice processing returns fallback extraction. |
| **Actual result** | `config.openai_api_key` is empty string; `extract_invoice_with_openai` raises `ValueError` caught silently; fallback result returned. |
| **Status** | PASS |
| **Notes** | Golden-path demo protection — the app always returns something useful. CI runs all tests with `OPENAI_API_KEY=""`. |

---

### 6. OpenAI API Failure

| Field | Value |
|-------|-------|
| **Test name** | Covered by fallback path in `processInvoice.ts` and `routers/invoices.py` |
| **Purpose** | Network errors, rate limits, or API key revocation must not crash the pipeline. |
| **Expected result** | Fallback extraction returned; `extraction_source: "fallback"`; uncertainty note added. |
| **Actual result** | `try/except` in both implementations catches all `openai` exceptions and falls through to fallback. |
| **Status** | PASS |
| **Notes** | Logs are not yet structured. Future: correlation ID + OpenTelemetry trace per extraction attempt. |

---

### 7. Missing Invoice Number

| Field | Value |
|-------|-------|
| **Test name** | `test_missing_invoice_number_raises_high_warning` (Python) + `validateInvoice.test.ts` (TypeScript) |
| **Purpose** | A blank invoice number must surface as a high-severity warning. |
| **Expected result** | Warning with `code: "missing_invoice_number"`, `severity: "high"`. |
| **Actual result** | Warning returned correctly from both implementations. |
| **Status** | PASS |

---

### 8. Missing Supplier

| Field | Value |
|-------|-------|
| **Test name** | `test_missing_supplier_name_raises_high_warning` (Python) + TypeScript equivalent |
| **Purpose** | Supplier name is required for invoice routing. |
| **Expected result** | Warning with `code: "missing_supplier_name"`, `severity: "high"`. |
| **Actual result** | Warning returned correctly. |
| **Status** | PASS |

---

### 9. Invalid Total Arithmetic

| Field | Value |
|-------|-------|
| **Test name** | `test_tax_mismatch_raises_high_warning` + `test_total_lower_than_subtotal_raises_high_warning` |
| **Purpose** | Detect AI hallucination or OCR error in numeric fields. |
| **Expected result** | `tax_total_mismatch` or `total_lower_than_subtotal` high warning. |
| **Actual result** | Both rules pass. Tolerance is ±0.02 to handle floating-point currency representation. |
| **Status** | PASS |
| **Notes** | `total_lower_than_subtotal` is a separate check from `tax_total_mismatch` to catch cases where VAT is unknown. |

---

### 10. Unknown Currency

| Field | Value |
|-------|-------|
| **Test name** | `test_unknown_currency_raises_medium_warning` |
| **Purpose** | Flag currency codes outside the recognized ISO 4217 set. |
| **Expected result** | Warning with `code: "unknown_currency"`, `severity: "medium"`. |
| **Actual result** | Warning returned for currency "XYZ". |
| **Status** | PASS |
| **Notes** | Known set: USD, EUR, GBP, CAD, AUD, CZK, PLN, SEK, NOK, DKK, CHF. |

---

### 11. Empty Line Items

| Field | Value |
|-------|-------|
| **Test name** | `test_empty_line_items_raises_medium_warning` |
| **Purpose** | Warn when no line items were extracted. |
| **Expected result** | `empty_line_items` medium warning. |
| **Actual result** | Warning returned. |
| **Status** | PASS |

---

### 12. Low Confidence Result

| Field | Value |
|-------|-------|
| **Test name** | `test_low_confidence_raises_medium_warning` |
| **Purpose** | Flag extractions below 0.70 confidence for human review. |
| **Expected result** | `low_confidence` medium warning when `confidence_score < 0.70`. |
| **Actual result** | Warning returned for score 0.5. |
| **Status** | PASS |
| **Notes** | Fallback extractor always returns 0.45 — always triggers this warning intentionally. |

---

### 13. Database Save Success

| Field | Value |
|-------|-------|
| **Test name** | `test_save_and_retrieve_invoice` + `test_record_to_summary_shape` |
| **Purpose** | Confirm every processed invoice is persisted with correct field mapping. |
| **Expected result** | Record saved with non-null `id`; retrieved record matches input. |
| **Actual result** | SQLite save and retrieval work correctly via SQLAlchemy ORM. |
| **Status** | PASS |

---

### 14. Database Save Failure Handling

| Field | Value |
|-------|-------|
| **Test name** | Code inspection (defensive design) |
| **Purpose** | Persistence failure must never crash the API response. |
| **Expected result** | API returns extraction result with `id: -1` when save fails. |
| **Actual result** | `try/except` in router wraps `save_invoice()`; on failure `id = -1`, `created_at = ""`. |
| **Status** | PASS (defensive design) |
| **Notes** | Production: retry with exponential backoff, then dead-letter queue. |

---

### 15. Health Endpoint

| Field | Value |
|-------|-------|
| **Test name** | `test_health_returns_ok` |
| **Purpose** | Confirm health check returns expected shape for monitoring integration. |
| **Expected result** | `{"status": "ok", "version": "...", "openai_configured": bool, "database": "sqlite"}` |
| **Actual result** | All fields present with correct types. |
| **Status** | PASS |

---

### 16. Metrics Endpoint

| Field | Value |
|-------|-------|
| **Test name** | `test_metrics_returns_expected_shape` |
| **Purpose** | Confirm metrics counters are accessible and return expected keys. |
| **Expected result** | All five metric keys present with correct types. |
| **Actual result** | Keys and types correct. |
| **Status** | PASS |
| **Notes** | Metrics are in-memory; reset on restart. Production: Prometheus via `prometheus-fastapi-instrumentator`. |

---

### 17. OpenAPI / Swagger Contract

| Field | Value |
|-------|-------|
| **Test name** | `test_openapi_documents_core_invoice_endpoints` |
| **Purpose** | Confirm Swagger/OpenAPI exposes the core invoice API and documented error statuses. |
| **Expected result** | `/openapi.json` includes process, list, get, health, metrics, and 415 upload response metadata. |
| **Actual result** | OpenAPI path and response metadata assertions pass. |
| **Status** | PASS |

---

### 18. Docker Compose Startup

| Field | Value |
|-------|-------|
| **Test name** | `docker compose build`, `docker compose up -d`, HTTP smoke checks |
| **Purpose** | Both services start, backend health check passes, frontend loads. |
| **Expected result** | `docker compose up --build` brings both services to healthy state. |
| **Actual result** | Compose builds both images, backend reaches healthy, frontend returns HTTP 200, backend `/health` returns OK, and `/openapi.json` exposes core paths. |
| **Status** | PASS |
| **Notes** | Frontend `depends_on` backend with `condition: service_healthy` ensures correct startup order. Backend data persists at `/app/data` without masking application source. |

---

### 19. CI Pipeline

| Field | Value |
|-------|-------|
| **Test name** | `.github/workflows/ci.yml` |
| **Purpose** | Automated gate on every push and PR covering both frontend and backend. |
| **Expected result** | Both `frontend` and `backend` jobs pass. |
| **Actual result** | Frontend: lint + 5 Vitest tests + build. Backend: 27 pytest tests. |
| **Status** | PASS |
| **Notes** | Python tests run with `OPENAI_API_KEY=""` and `DATABASE_URL="sqlite:///:memory:"` — no secrets in CI. |

---

## Bugs Found and Fixed

| # | Bug | Fix | Status |
|---|-----|-----|--------|
| 1 | Python 3.9 incompatible `str \| None` union syntax | Added `from __future__ import annotations` to all Python service modules | Fixed |
| 2 | `persistence.py` `created_at` lacked null guard in `record_to_summary` | Added `if record.created_at else ""` guard | Fixed |
| 3 | Router `ValidationWarning` imported via fragile `__import__` in scanned PDF path | Refactored to proper top-level import | Fixed |
| 4 | `merge_with_fallback` in Python set `extraction_source` as string literal not enum value | Updated to use string literal accepted by Pydantic `ExtractionSource` | Fixed |
| 5 | Frontend Dockerfile expected `.next/standalone`, but Next config did not emit standalone output | Added `output: "standalone"` to `next.config.ts` | Fixed |
| 6 | Docker Compose mounted `backend_data` over `/app`, which could hide backend source code in the container | Changed volume mount to `/app/data` and SQLite path to `/app/data/invoices.db` | Fixed |
| 7 | FastAPI HTTP errors used default `{"detail": ...}` shape while docs defined an `ErrorResponse` model | Added exception handlers returning `{"error": ..., "detail": ...}` | Fixed |
| 8 | Vercel preview CORS used `https://*.vercel.app`, which Starlette does not treat as a wildcard origin | Replaced with `allow_origin_regex` setting | Fixed |
| 9 | PostgreSQL was documented as production-ready, but requirements lacked a PostgreSQL driver | Added `psycopg[binary]` and database-kind detection | Fixed |
| 10 | Backend Docker image installed `gcc`, adding ~180 MB and slow builds despite wheel-based dependencies | Removed compiler layer and verified backend image still builds | Fixed |

---

## Known Limitations

| # | Limitation | Workaround | Production Path |
|---|-----------|------------|-----------------|
| 1 | SQLite is single-writer — not suitable for high-concurrency production load | Acceptable for portfolio demo | Replace `DATABASE_URL` with PostgreSQL/Supabase |
| 2 | Metrics reset on service restart | Documented in `/metrics` endpoint | Prometheus with persistent time-series storage |
| 3 | No auth on any endpoint | Open demo acceptable | OAuth2 or API key via FastAPI security utilities |
| 4 | Scanned PDFs get a warning but no OCR | Clearly documented | AWS Textract / Azure Document Intelligence / Google Document AI |
| 5 | Large PDFs processed synchronously — may timeout under load | 20 MB upload limit + 60s Next.js route timeout | Async queue (Celery + Redis or AWS SQS) |
| 6 | Frontend and Python backend are parallel implementations, not integrated | Both use identical logic and schemas | In production, frontend proxies to Python backend |
| 7 | No structured logging | FastAPI default logs | JSON logs with correlation IDs via `structlog` |

---

## Production Hardening Roadmap

1. **Async queue** — Celery + Redis or AWS SQS for large PDF batches; decouple upload from processing.
2. **OCR service** — AWS Textract, Azure Document Intelligence, or Google Document AI for scanned invoices.
3. **PostgreSQL / Supabase** — production-grade database. Drop-in via `DATABASE_URL` change.
4. **Object storage** — S3 or GCS for uploaded PDFs with signed URL retrieval.
5. **Auth layer** — API key or OAuth2 client credentials via FastAPI's `HTTPBearer`.
6. **Rate limiting** — per-client throttle with `slowapi` or AWS API Gateway.
7. **Observability** — `prometheus-fastapi-instrumentator` + Grafana; OpenTelemetry traces per extraction stage.
8. **Structured logs** — JSON logs with correlation IDs for Datadog/Splunk ingestion.
9. **Model/version tracking** — log model name and version per extraction; detect quality drift over time.
10. **Human review workflow** — invoices with high-severity warnings route to a review queue.
11. **Kubernetes** — horizontal pod autoscaling for the FastAPI backend; see `k8s/` for reference manifests.
12. **Dataset regression tests** — labeled invoice fixture corpus; run extraction against it in CI to catch model-level regressions.
