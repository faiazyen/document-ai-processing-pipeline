# Python FastAPI Backend — Swagger / OpenAPI Reference

The Document AI Processing Pipeline exposes a production-style REST API via **FastAPI**, which auto-generates OpenAPI 3.1 documentation and an interactive Swagger UI.

## Swagger UI

When running locally:

```
http://localhost:8000/docs
```

ReDoc alternative:

```
http://localhost:8000/redoc
```

---

## Endpoints

### POST /process-invoice

Upload a PDF invoice for end-to-end AI extraction and validation.

**Request** — `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | PDF file | Yes | Invoice PDF, max 20 MB |

**Response 200** — `application/json`

```json
{
  "id": 42,
  "filename": "acme-invoice-042.pdf",
  "extraction": {
    "document_type": "invoice",
    "supplier_name": "Acme Textiles GmbH",
    "supplier_country": "DE",
    "buyer_name": "Merch Maverick Ltd",
    "invoice_number": "INV-2024-042",
    "invoice_date": "2024-03-15",
    "due_date": "2024-04-15",
    "currency": "EUR",
    "subtotal": 1200.00,
    "vat_amount": 240.00,
    "total_amount": 1440.00,
    "line_items": [
      {
        "description": "Custom Polo Shirts 100% Cotton",
        "quantity": 100,
        "unit_price": 12.00,
        "total": 1200.00
      }
    ],
    "payment_terms": "Net 30",
    "confidence_score": 0.91,
    "validation_warnings": [],
    "extraction_source": "openai",
    "processing_ms": 1342.5
  },
  "raw_text_preview": "INVOICE\nFrom: Acme Textiles GmbH\n...",
  "created_at": "2024-03-15T14:32:01.000000+00:00"
}
```

**Error response shape**

```json
{
  "error": "Only PDF uploads are accepted.",
  "detail": null
}
```

**Error cases**

| Status | Reason |
|--------|--------|
| 400 | Non-PDF file type |
| 400 | Empty file |
| 413 | File exceeds 20 MB |
| 415 | Unsupported upload content type |
| 422 | PDF parsing failure (corrupt file) |
| 500 | Unexpected server error |

---

### GET /invoices

Return a list of all processed invoice summaries from the database, ordered newest first.

**Response 200**

```json
[
  {
    "id": 42,
    "filename": "acme-invoice-042.pdf",
    "document_type": "invoice",
    "supplier_name": "Acme Textiles GmbH",
    "buyer_name": "Merch Maverick Ltd",
    "invoice_number": "INV-2024-042",
    "total_amount": 1440.00,
    "currency": "EUR",
    "confidence_score": 0.91,
    "extraction_source": "openai",
    "processing_ms": 1342.5,
    "created_at": "2024-03-15T14:32:01.000000+00:00"
  }
]
```

---

### GET /invoices/{id}

Return full extraction result for a single invoice by database ID.

**Path parameter**

| Param | Type | Description |
|-------|------|-------------|
| id | integer | Invoice database ID |

**Error cases**

| Status | Reason |
|--------|--------|
| 404 | Invoice not found |

---

### GET /health

Service health and configuration status.

**Response 200**

```json
{
  "status": "ok",
  "version": "1.0.0",
  "openai_configured": true,
  "database": "sqlite"
}
```

`openai_configured` is `false` when `OPENAI_API_KEY` is missing. The service still processes invoices via fallback extraction.

---

### GET /metrics

In-memory processing counters. Resets on service restart.

**Response 200**

```json
{
  "processed_documents": 17,
  "failed_documents": 1,
  "average_processing_ms": 1253.4,
  "fallback_rate": 0.235,
  "validation_warning_count": 34
}
```

| Field | Description |
|-------|-------------|
| processed_documents | Total successful invoice processing calls |
| failed_documents | Total failed processing calls |
| average_processing_ms | Mean end-to-end processing time in ms |
| fallback_rate | Fraction of documents that used fallback (0–1) |
| validation_warning_count | Cumulative count of warnings across all invoices |

---

## Testing Locally

```bash
# Start the backend
cd services/ai-api
uvicorn app.main:app --reload --port 8000

# Health check
curl http://localhost:8000/health

# Upload a PDF (replace with a real PDF path)
curl -X POST http://localhost:8000/process-invoice \
  -F "file=@../../samples/sample-invoice.pdf"

# List invoices
curl http://localhost:8000/invoices

# Metrics
curl http://localhost:8000/metrics
```

---

## Why OpenAPI Matters for Production AI Systems

1. **Contract-first design** — The schema is the source of truth. Downstream consumers (frontend, integrations, CI tests) can validate against it automatically.

2. **Versioning** — FastAPI's `version` field and endpoint prefixing support `v1`/`v2` coexistence for non-breaking API evolution.

3. **Auto-generated client SDKs** — OpenAPI JSON at `/openapi.json` can be fed to `openapi-generator` to produce typed Python, TypeScript, Go, or Java clients without manual maintenance.

4. **Interactive testing** — Swagger UI lets stakeholders and QA engineers test endpoints without writing code, reducing feedback loop time.

5. **Integration with API gateways** — AWS API Gateway, Kong, and Azure APIM all consume OpenAPI specs natively for routing, auth, and rate limiting.

6. **Observability hooks** — Tools like Stoplight, Postman, and Apidog can monitor spec drift and alert when actual responses deviate from the documented contract.
