import { extractTextFromPdf, validatePdfUpload } from "./extractText";
import { fallbackExtractInvoice, mergeWithFallback } from "./fallbackExtractor";
import { extractInvoiceWithOpenAI } from "./openai";
import { type InvoiceProcessResponse } from "./schemas";
import { validateInvoice } from "./validateInvoice";

function shouldUseFallback(warningCodes: string[], confidence: number) {
  return (
    confidence < 0.74 ||
    warningCodes.some((code) =>
      [
        "missing_invoice_number",
        "missing_supplier_name",
        "missing_invoice_date",
        "missing_total_amount",
      ].includes(code),
    )
  );
}

export async function processInvoiceFile(file: File): Promise<InvoiceProcessResponse> {
  const startedAt = Date.now();
  validatePdfUpload(file);

  const buffer = new Uint8Array(await file.arrayBuffer());
  const { text } = await extractTextFromPdf(buffer);
  const fallback = fallbackExtractInvoice(text);

  let extraction = fallback;
  let extractionSource: InvoiceProcessResponse["extraction_source"] = "fallback";

  try {
    const openAiExtraction = await extractInvoiceWithOpenAI(text);
    const initialWarnings = validateInvoice(openAiExtraction);
    const warningCodes = initialWarnings.map((warning) => warning.code);

    if (shouldUseFallback(warningCodes, openAiExtraction.confidence_score)) {
      extraction = mergeWithFallback(openAiExtraction, fallback);
      extractionSource = "openai_with_fallback";
    } else {
      extraction = openAiExtraction;
      extractionSource = "openai";
    }
  } catch (error) {
    extraction = {
      ...fallback,
      uncertainty_notes: [
        ...fallback.uncertainty_notes,
        error instanceof Error
          ? `OpenAI extraction unavailable: ${error.message}`
          : "OpenAI extraction unavailable.",
      ],
    };
    extractionSource = "fallback";
  }

  const validationWarnings = validateInvoice(extraction);

  return {
    success: true,
    document_type: extraction.document_type,
    extraction,
    validation_warnings: validationWarnings,
    confidence_score: extraction.confidence_score,
    extraction_source: extractionSource,
    raw_text_preview: text.slice(0, 1600),
    processing_ms: Date.now() - startedAt,
  };
}
