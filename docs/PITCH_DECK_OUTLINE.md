# Pitch Deck Outline

## Slide 1: Problem

B2B merchandise invoices arrive as PDFs with inconsistent layouts. Manual data entry is slow, error-prone, and hard to audit.

## Slide 2: Solution

Document AI pipeline that extracts invoice fields, validates financial consistency, and returns explainable JSON.

## Slide 3: Architecture

PDF upload -> text extraction -> OpenAI structured extraction -> fallback extraction -> deterministic validation -> dashboard JSON output.

## Slide 4: Reliability

The model is not blindly trusted. Fallback rules fill critical gaps and validation warnings flag missing or inconsistent values.

## Slide 5: Engineering Quality

TypeScript schemas, pure validation functions, unit tests, GitHub Actions CI, and Vercel-ready deployment.

## Slide 6: Demo Flow

Upload invoice, watch pipeline stages, review confidence, inspect warnings, copy final JSON.

## Slide 7: Production Roadmap

OCR, persistent audit logs, field-level confidence, human review queue, observability, and regression evaluation datasets.
