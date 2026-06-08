# Project Plan

## Project Brief

**Repo name:** `document-ai-processing-pipeline`  
**Branding:** by MaverickIQ  
**Use case:** business invoices from The Merch Maverick B2B merchandise platform  
**AI layer:** OpenAI API extraction with deterministic rule-based fallback  
**UI:** dark, elegant, minimal, technical startup-dashboard style  
**Deployment target:** Vercel demo UI  
**Final deliverables:** public GitHub repo, Vercel demo, test/debugging audit, interview pitch deck

## Billing And Secret Handling Note

ChatGPT subscription billing and OpenAI API platform billing are separate. The project should use an `OPENAI_API_KEY` stored safely in `.env.local` for local development and in Vercel environment variables for deployment.

Secrets must never be committed to GitHub.

## What We Are Building

A portfolio-grade Document AI Processing Pipeline:

1. Upload a business invoice PDF.
2. Extract raw text from the PDF.
3. Classify the document as an invoice.
4. Extract structured invoice fields.
5. Run deterministic validation.
6. Surface missing fields, risky values, confidence score, and warnings.
7. Display the structured JSON output.
8. Store or export sample outputs.
9. Explain the system like an AI infrastructure project.

## Product Goals

- Demonstrate a realistic AI document processing workflow.
- Show practical OpenAI API usage with structured output.
- Include fallback extraction for reliability.
- Make validation a first-class part of the system.
- Present the work cleanly for portfolio and interview use.
- Keep the UI polished but engineering-focused.

## Non-Goals For The First Build

- Full production authentication.
- Multi-tenant document storage.
- Payment or billing integration.
- Human review queue.
- OCR for scanned image-only PDFs unless added as a later enhancement.
- Enterprise-grade audit logging beyond demo-quality logs and sample outputs.

## Tech Stack

### Frontend And Deployment

- Next.js
- TypeScript
- Tailwind CSS
- Dark minimalist UI
- Vercel deployment

### AI Extraction

- OpenAI API
- Structured JSON output
- Prompt template for B2B invoice extraction
- Rule-based fallback extraction with regex

### Document Processing

- PDF text extraction
- Invoice-focused text cleanup
- Sample invoice fixtures

### Testing

- Vitest or Jest for frontend and API logic
- Pytest only if a Python local pipeline is intentionally added later
- Manual QA checklist
- Debugging audit file

### Engineering Proof

- GitHub Actions CI
- `.env.example`
- README
- Architecture documentation
- `TESTING_AND_DEBUGGING_AUDIT.md`
- `INTERVIEW_WALKTHROUGH.md`

## Delivery Milestones

### Milestone 1: Planning And Repo Skeleton

- Confirm product scope.
- Create Next.js project structure.
- Add README, architecture docs, schema docs, and setup notes.
- Add `.env.example`.

### Milestone 2: Frontend Demo Shell

- Build dark dashboard layout.
- Add upload panel.
- Add pipeline status visualization.
- Add empty, loading, success, and error states.
- Add JSON viewer.

### Milestone 3: Document Processing

- Accept uploaded invoice PDFs.
- Extract readable text.
- Normalize whitespace.
- Return readable extraction errors when text cannot be parsed.

### Milestone 4: AI Extraction

- Add secure OpenAI server-side integration.
- Add invoice extraction prompt.
- Return structured JSON matching the schema.
- Add confidence scoring instructions.

### Milestone 5: Validation And Fallback

- Add deterministic validation rules.
- Add fallback extraction for critical invoice fields.
- Merge AI and fallback results carefully.
- Add unit tests.

### Milestone 6: QA And Debugging Audit

- Test golden-path upload.
- Test invalid file.
- Test missing fields.
- Test low-confidence extraction.
- Test OpenAI API failure behavior.
- Document findings and fixes.

### Milestone 7: Portfolio Packaging

- Finalize README.
- Add architecture diagram.
- Add interview walkthrough.
- Add pitch deck outline.
- Prepare public GitHub repo.
- Deploy to Vercel.

