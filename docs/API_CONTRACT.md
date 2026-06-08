# API Contract

## `POST /api/process-invoice`

Processes a single text-based PDF invoice.

### Request

Content type: `multipart/form-data`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `file` | PDF file | Yes | Must be a PDF and <= 8 MB |

### Success Response

```json
{
  "success": true,
  "document_type": "invoice",
  "extraction": {},
  "validation_warnings": [],
  "confidence_score": 0.91,
  "extraction_source": "openai_with_fallback",
  "raw_text_preview": "Invoice Number...",
  "processing_ms": 1840
}
```

`extraction_source` can be:

- `openai`
- `fallback`
- `openai_with_fallback`

### Error Response

```json
{
  "success": false,
  "error": "Upload must be a PDF invoice.",
  "validation_warnings": []
}
```

### Expected Failure Modes

- invalid file type
- PDF larger than the demo limit
- empty PDF
- scanned image-only PDF with no readable text
- parsing failure

OpenAI failures do not fail the request if PDF text was extracted. The API falls back to deterministic extraction and includes uncertainty notes.
