# Project Structure

This is the planned final repository structure for `document-ai-processing-pipeline`.

```text
document-ai-processing-pipeline/
├── app/
│   ├── page.tsx
│   ├── layout.tsx
│   ├── api/
│   │   └── process-invoice/
│   │       └── route.ts
│   └── globals.css
├── components/
│   ├── UploadPanel.tsx
│   ├── ExtractionResult.tsx
│   ├── ValidationPanel.tsx
│   ├── JsonViewer.tsx
│   └── PipelineSteps.tsx
├── lib/
│   ├── openai.ts
│   ├── invoicePrompt.ts
│   ├── extractText.ts
│   ├── validateInvoice.ts
│   ├── fallbackExtractor.ts
│   └── schemas.ts
├── samples/
│   ├── sample-invoice-001.pdf
│   └── sample-output.json
├── tests/
│   ├── validateInvoice.test.ts
│   └── fallbackExtractor.test.ts
├── docs/
│   ├── ARCHITECTURE.md
│   ├── TESTING_AND_DEBUGGING_AUDIT.md
│   ├── INTERVIEW_WALKTHROUGH.md
│   └── PITCH_DECK_OUTLINE.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env.example
├── README.md
├── package.json
└── vercel.json
```

## File Responsibilities

### App Router

- `app/page.tsx`: main dashboard experience.
- `app/layout.tsx`: app shell metadata and global layout.
- `app/api/process-invoice/route.ts`: secure server-side invoice processing endpoint.
- `app/globals.css`: global theme styles.

### Components

- `UploadPanel.tsx`: PDF upload, file state, and submit controls.
- `ExtractionResult.tsx`: structured invoice field display.
- `ValidationPanel.tsx`: warnings, failed checks, and risk summary.
- `JsonViewer.tsx`: formatted JSON result panel.
- `PipelineSteps.tsx`: visual processing pipeline state.

### Library Layer

- `openai.ts`: OpenAI client setup and server-only helper.
- `invoicePrompt.ts`: extraction prompt and schema instructions.
- `extractText.ts`: PDF text extraction and cleanup.
- `validateInvoice.ts`: deterministic invoice validation.
- `fallbackExtractor.ts`: regex fallback for critical fields.
- `schemas.ts`: shared TypeScript types and validation schemas.

### Samples

- `sample-invoice-001.pdf`: demo invoice fixture.
- `sample-output.json`: expected or sample extraction output.

### Tests

- `validateInvoice.test.ts`: validation rule coverage.
- `fallbackExtractor.test.ts`: fallback extraction coverage.

### Docs

- `ARCHITECTURE.md`: system architecture, flow, and API contract.
- `TESTING_AND_DEBUGGING_AUDIT.md`: QA evidence and known limitations.
- `INTERVIEW_WALKTHROUGH.md`: portfolio interview explanation.
- `PITCH_DECK_OUTLINE.md`: short presentation outline.

