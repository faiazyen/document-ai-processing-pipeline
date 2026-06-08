import { PDFParse } from "pdf-parse";

export const MAX_PDF_BYTES = 8 * 1024 * 1024;

export type TextExtractionResult = {
  text: string;
  pageCount?: number;
};

export function validatePdfUpload(file: File) {
  if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
    throw new Error("Upload must be a PDF invoice.");
  }

  if (file.size === 0) {
    throw new Error("Uploaded PDF is empty.");
  }

  if (file.size > MAX_PDF_BYTES) {
    throw new Error("PDF is larger than the 8 MB demo processing limit.");
  }
}

export function normalizeInvoiceText(text: string) {
  return text
    .replace(/\u0000/g, "")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

export async function extractTextFromPdf(data: Uint8Array): Promise<TextExtractionResult> {
  const parser = new PDFParse({ data });

  try {
    const result = await parser.getText();
    const text = normalizeInvoiceText(result.text);

    if (text.length < 20) {
      throw new Error(
        "No readable text was found. This demo expects text-based PDFs, not scanned image-only invoices.",
      );
    }

    return {
      text,
      pageCount: result.pages?.length,
    };
  } finally {
    await parser.destroy();
  }
}
