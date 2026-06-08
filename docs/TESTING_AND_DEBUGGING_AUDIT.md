# Testing And Debugging Audit

## Automated Checks

CI is configured to run:

```bash
npm ci
npm run lint
npm test
npm run build
```

## Covered By Unit Tests

- fallback extraction for invoice number, dates, buyer, totals, currency, and line items
- fallback merge behavior
- missing critical field warnings
- tax/total mismatch warning
- clean invoice with no warnings

## Manual QA Checklist

- Upload a valid text-based PDF invoice.
- Upload a non-PDF file and confirm a readable error.
- Upload a scanned image-only PDF and confirm the readable-text error.
- Run without `OPENAI_API_KEY` and confirm fallback result still renders.
- Run with `OPENAI_API_KEY` and confirm OpenAI extraction source.
- Verify validation warnings and JSON output match the same response.

## Known Limitations

- OCR is not implemented for scanned documents.
- No document persistence or audit log database is included.
- The fallback parser is intentionally conservative and invoice-template dependent.
- Field-level confidence is not implemented; confidence is document-level.

## Production Hardening Path

- Add OCR via a dedicated service or model.
- Persist document, extraction, warnings, and model metadata.
- Add tracing around each pipeline stage.
- Add a human review queue for high-severity warnings.
- Build a fixture corpus and regression test extraction quality.
