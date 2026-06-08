# Execution Checklist

## Phase 1: Next.js App And Dark UI

- [x] Scaffold Next.js App Router with TypeScript and Tailwind.
- [x] Build dark technical dashboard shell.
- [x] Add upload, pipeline, extraction, warning, and JSON panels.
- [x] Keep components under 300 LOC.

## Phase 2: PDF Upload And Text Extraction

- [x] Add PDF-only multipart upload.
- [x] Enforce 8 MB demo size limit.
- [x] Extract readable text with `pdf-parse`.
- [x] Return readable errors for image-only PDFs.

## Phase 3: OpenAI Structured Extraction

- [x] Add server-only OpenAI client.
- [x] Read `OPENAI_API_KEY` from environment variables only.
- [x] Use Zod-backed structured response parsing.
- [x] Support configurable `OPENAI_MODEL`.

## Phase 4: Validation Engine And Fallback Extractor

- [x] Add deterministic warning engine.
- [x] Add regex fallback for critical invoice values.
- [x] Merge fallback values when model confidence or completeness is weak.

## Phase 5: Tests And CI

- [x] Add Vitest unit tests.
- [x] Add GitHub Actions CI for install, lint, test, and build.

## Phase 6: Vercel Deployment Readiness

- [x] Add `vercel.json`.
- [x] Document required environment variables.
- [x] Keep PDF/OpenAI processing in Node.js runtime.

## Phase 7: Testing And Debugging Audit

- [x] Add audit document with completed and pending checks.

## Phase 8: Documentation Cleanup

- [x] Add architecture notes.
- [x] Add testing and debugging audit.
