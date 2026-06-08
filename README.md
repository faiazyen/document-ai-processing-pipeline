# Document AI Processing Pipeline by MaverickIQ

A portfolio-grade Document AI pipeline for B2B merchandise invoices from The Merch Maverick. The app uploads PDF invoices, extracts readable text, runs structured OpenAI extraction, fills critical gaps with deterministic fallback rules, validates invoice consistency, and renders the final JSON payload.

## Why This Exists

This project is optimized for an AI Platform Engineer portfolio conversation: document processing, model-style structured extraction, deterministic validation, fallback reliability, CI/CD, and deployment readiness.

## Stack

- Next.js 16 App Router
- TypeScript
- Tailwind CSS v4
- OpenAI API with structured Zod response parsing
- `pdf-parse` v2 text extraction
- Deterministic validation and regex fallback extraction
- Vitest unit tests
- GitHub Actions CI
- Vercel-ready configuration

## Pipeline

```text
PDF upload
  -> text extraction
  -> OpenAI structured extraction
  -> fallback merge when confidence or critical fields are weak
  -> deterministic validation
  -> confidence, warnings, raw preview, final JSON
```

## Local Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

Set `OPENAI_API_KEY` in `.env.local`. Do not commit secrets. `OPENAI_MODEL` is optional and defaults to `gpt-4.1-mini`.

If `OPENAI_API_KEY` is missing or the OpenAI request fails, the API still returns a fallback extraction with validation warnings.

## Commands

```bash
npm run dev
npm run lint
npm test
npm run build
```

## API

`POST /api/process-invoice`

- Request: `multipart/form-data` with `file` as a PDF.
- Response: structured invoice JSON, confidence score, extraction source, validation warnings, processing time, and raw text preview.

See [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Invoice Schema](docs/INVOICE_SCHEMA.md)
- [API Contract](docs/API_CONTRACT.md)
- [Execution Checklist](docs/EXECUTION_CHECKLIST.md)
- [Testing and Debugging Audit](docs/TESTING_AND_DEBUGGING_AUDIT.md)
- [Interview Walkthrough](docs/INTERVIEW_WALKTHROUGH.md)
- [Pitch Deck Outline](docs/PITCH_DECK_OUTLINE.md)

## Production Readiness Notes

This is intentionally scoped as a portfolio demo, but the architecture leaves clean seams for OCR, document storage, audit logs, human review queues, and observability. Secrets stay server-side, validation is deterministic, and CI runs lint, tests, and build.
