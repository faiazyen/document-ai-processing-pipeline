import { describe, expect, it } from "vitest";
import {
  MAX_PDF_BYTES,
  normalizeInvoiceText,
  validatePdfUpload,
} from "../src/lib/extractText";

describe("validatePdfUpload", () => {
  it("accepts a PDF by MIME type", () => {
    const file = new File(["%PDF-1.7"], "invoice", {
      type: "application/pdf",
    });

    expect(() => validatePdfUpload(file)).not.toThrow();
  });

  it("accepts a PDF by filename when MIME type is missing", () => {
    const file = new File(["%PDF-1.7"], "invoice.pdf", {
      type: "",
    });

    expect(() => validatePdfUpload(file)).not.toThrow();
  });

  it("rejects non-PDF uploads", () => {
    const file = new File(["plain text"], "invoice.txt", {
      type: "text/plain",
    });

    expect(() => validatePdfUpload(file)).toThrow("Upload must be a PDF invoice.");
  });

  it("rejects empty PDFs", () => {
    const file = new File([], "empty.pdf", {
      type: "application/pdf",
    });

    expect(() => validatePdfUpload(file)).toThrow("Uploaded PDF is empty.");
  });

  it("rejects PDFs above the demo processing limit", () => {
    const file = new File([new Uint8Array(MAX_PDF_BYTES + 1)], "large.pdf", {
      type: "application/pdf",
    });

    expect(() => validatePdfUpload(file)).toThrow(
      "PDF is larger than the 8 MB demo processing limit.",
    );
  });
});

describe("normalizeInvoiceText", () => {
  it("removes null bytes and normalizes whitespace without flattening paragraphs", () => {
    const text = "Invoice\u0000   Number:\tINV-101\n\n\n\nTotal   USD\t42.00";

    expect(normalizeInvoiceText(text)).toBe(
      "Invoice Number: INV-101\n\nTotal USD 42.00",
    );
  });
});
