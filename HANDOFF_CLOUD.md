# Cloud Handoff: Document AI Processing Pipeline

## Project Location

Local folder:

```text
/Users/faiazyen/Desktop/Merch Maverick MAIN LOCAL/ai-processing-pipeline by MaverickIQ
```

GitHub repository:

```text
https://github.com/faiazyen/document-ai-processing-pipeline
```

This is a standalone public repository under Faiaz's GitHub profile. It is not part of the Merch Maverick repo and is not under a MaverickIQ organization.

## Current State

The project was started from scratch in the folder above and implemented as a portfolio-grade Document AI Processing Pipeline for B2B merchandise invoices.

Implemented:

- Next.js 16 App Router app
- TypeScript
- Tailwind CSS v4 dark technical UI
- PDF upload UI
- `POST /api/process-invoice` route
- PDF text extraction with `pdf-parse`
- OpenAI structured extraction using `OPENAI_API_KEY` from environment variables only
- Zod invoice schema
- deterministic validation engine
- rule-based fallback extractor
- fallback merge when confidence or critical fields are weak
- confidence score and validation warning rendering
- final JSON output viewer
- `.env.example`
- Vitest tests
- GitHub Actions CI
- Vercel-ready `vercel.json`
- architecture, API, schema, checklist, testing audit, interview walkthrough, and pitch deck docs

## Verification Completed

Commands passed locally:

```bash
npm run lint
npm test
npm run build
```

Test result:

```text
2 test files passed
5 tests passed
```

Local HTTP smoke check completed:

- `GET /` returned `200 OK`
- `POST /api/process-invoice` without multipart data returned a structured JSON error

The dev server was stopped after verification.

## Important Environment Notes

Required local or deployment variable:

```text
OPENAI_API_KEY
```

Optional:

```text
OPENAI_MODEL=gpt-4.1-mini
```

Do not commit real secrets. `.env*` files are ignored. `.env.example` is intentionally tracked.

If `OPENAI_API_KEY` is missing or OpenAI extraction fails, the API returns fallback extraction results with uncertainty notes instead of crashing the golden-path demo.

## Git Status At Handoff Creation

Before this handoff file was added, local `main` was clean and tracking:

```text
origin/main
```

Remote:

```text
origin https://github.com/faiazyen/document-ai-processing-pipeline.git
```

After creating this file, commit and push it if you want it available on GitHub:

```bash
git add HANDOFF_CLOUD.md
git commit -m "Add cloud handoff"
git push
```

## Recommended Next Tasks For Cloud

1. Deploy to Vercel as a new project from `faiazyen/document-ai-processing-pipeline`.
2. Add `OPENAI_API_KEY` to Vercel environment variables.
3. Run a production deployment and confirm it reaches `Ready`.
4. Upload a real text-based invoice PDF and verify extraction behavior.
5. Add one or two sanitized PDF fixtures if portfolio sharing allows it.
6. Consider adding OCR support for scanned invoices as the next major enhancement.
7. Add field-level confidence if the project needs to feel closer to a production document AI system.

## Key Files

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/API_CONTRACT.md`
- `docs/INVOICE_SCHEMA.md`
- `docs/EXECUTION_CHECKLIST.md`
- `docs/TESTING_AND_DEBUGGING_AUDIT.md`
- `docs/INTERVIEW_WALKTHROUGH.md`
- `docs/PITCH_DECK_OUTLINE.md`
- `src/app/api/process-invoice/route.ts`
- `src/lib/processInvoice.ts`
- `src/lib/openai.ts`
- `src/lib/extractText.ts`
- `src/lib/fallbackExtractor.ts`
- `src/lib/validateInvoice.ts`
- `src/lib/schemas.ts`

## Portfolio Positioning

Frame this as a mini Rossum-style invoice AI system:

- AI extraction is useful but not blindly trusted.
- Deterministic validation is first-class.
- Fallback extraction protects demo reliability.
- CI/CD and deployment readiness are included.
- Future production concerns are documented clearly.
