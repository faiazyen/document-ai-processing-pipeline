# Sub-Agent Execution Plan

This is the planned build sequence for future implementation work.

## 1. Product Architect Agent

### Task

Design the full product scope, user flow, system architecture, data schema, validation rules, and README structure for a portfolio-grade Document AI Processing Pipeline by MaverickIQ.

The project should process B2B invoice PDFs from The Merch Maverick use case, use the OpenAI API for structured extraction, include fallback rule-based extraction, and deploy a dark minimal Next.js demo to Vercel.

### Output

- `README.md`
- `docs/ARCHITECTURE.md`
- Invoice schema
- User flow
- API contract

## 2. Frontend Agent

### Task

Build a dark, elegant, minimal Next.js dashboard for the Document AI Processing Pipeline. It should include a PDF upload panel, processing state, pipeline step visualization, extracted invoice fields, validation warnings, confidence score, and JSON viewer.

### Output

- `app/page.tsx`
- UI components
- Responsive dark theme
- Empty, loading, success, and error states

## 3. AI Extraction Agent

### Task

Build the OpenAI invoice extraction layer. Create a secure API route that accepts extracted invoice text and returns structured JSON using the invoice schema. Add strong prompt instructions for reliable invoice extraction, confidence scoring, and validation-aware output.

Use `OPENAI_API_KEY`. Never expose secrets to the client.

### Output

- `lib/openai.ts`
- `lib/invoicePrompt.ts`
- API integration
- Safe error handling

## 4. Document Processing Agent

### Task

Implement PDF text extraction for uploaded invoice files. Extract raw text from PDF, clean the text, normalize whitespace, and pass it to the AI extraction layer. Add fallback handling when extraction fails or the document has no readable text.

### Output

- `lib/extractText.ts`
- PDF parsing
- Error handling
- Sample invoice testing

## 5. Validation Agent

### Task

Build a deterministic invoice validation engine. Validate extracted fields, detect missing or inconsistent values, calculate basic arithmetic checks, and return validation warnings. Add fallback regex extraction for critical fields like invoice number, date, currency, and total amount.

### Output

- `lib/validateInvoice.ts`
- `lib/fallbackExtractor.ts`
- Test cases

## 6. DevOps Agent

### Task

Add GitHub Actions CI, environment configuration, Vercel deployment readiness, `.env.example`, and clean setup documentation.

Ensure the repo can run locally with:

```text
npm install
npm run dev
npm test
```

These commands are planned for a future implementation phase and have not been run as part of this planning step.

### Output

- `.github/workflows/ci.yml`
- `.env.example`
- `vercel.json`
- Package scripts
- Deployment instructions

## 7. QA / Debugging Audit Agent

### Task

Test the project like a senior AI platform engineer. Run upload tests, API tests, validation tests, broken-document tests, missing-field tests, and OpenAI failure tests.

Document every issue found, fix applied, remaining limitation, and future improvement in `TESTING_AND_DEBUGGING_AUDIT.md`.

### Output

- `docs/TESTING_AND_DEBUGGING_AUDIT.md`
- Bug list
- Fixes
- Test results
- Known limitations

## 8. Interview Pitch Agent

### Task

Create an interview explanation for the project. Explain the problem, architecture, technical decisions, extraction flow, validation strategy, testing approach, limitations, and future improvements.

Make it suitable for explaining to Rossum as an AI Platform Engineer portfolio project.

### Output

- `docs/INTERVIEW_WALKTHROUGH.md`
- `docs/PITCH_DECK_OUTLINE.md`

