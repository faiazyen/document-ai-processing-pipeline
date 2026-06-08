# Interview Walkthrough

## 60-Second Summary

This is a document AI pipeline for B2B merchandise invoices. It extracts PDF text, asks OpenAI for a strict invoice schema, falls back to deterministic regex extraction when the model is unavailable or incomplete, validates financial consistency, and returns explainable JSON with confidence and warnings.

## Engineering Talking Points

- The AI layer is isolated behind `src/lib/openai.ts`.
- The deterministic validator is pure and unit-tested.
- The fallback extractor makes the demo resilient without pretending regex is enough for production.
- Secrets stay server-side in the Next.js route handler.
- The UI renders evidence: confidence, extraction source, warnings, and raw JSON.
- CI proves lint, tests, and production build.

## Rossum-Relevant Framing

Rossum-style systems need extraction quality, explainability, and operational reliability. This project shows the same mindset in miniature: model output is validated, missing fields are surfaced, fallbacks are explicit, and the code is organized for future OCR, review queues, and monitoring.

## Tradeoffs

- I chose text-based PDFs first to keep the MVP focused and testable.
- I used OpenAI structured output for schema adherence, then deterministic validation for trust.
- I did not persist uploads because the portfolio objective is processing architecture, not document storage.

## Next Iteration

Add OCR, field-level confidence, dataset evaluation, and a human review UI for high-risk invoices.
