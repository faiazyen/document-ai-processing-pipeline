import { describe, expect, it } from "vitest";
import { fallbackExtractInvoice, mergeWithFallback } from "../src/lib/fallbackExtractor";
import { emptyInvoiceExtraction } from "../src/lib/schemas";

const invoiceText = `
Northstar Print Studio
Invoice Number: MM-2026-0042
Invoice Date: 2026-06-08
Due Date: 2026-06-30
Bill To: Atlas Retail Group
Payment Terms: Net 30
Custom Embroidered Hoodies 120 24.50 2940.00
Subtotal USD 2940.00
VAT USD 588.00
Total Due USD 3528.00
`;

describe("fallbackExtractInvoice", () => {
  it("extracts critical invoice fields from readable text", () => {
    const result = fallbackExtractInvoice(invoiceText);

    expect(result.document_type).toBe("invoice");
    expect(result.invoice_number).toBe("MM-2026-0042");
    expect(result.invoice_date).toBe("2026-06-08");
    expect(result.due_date).toBe("2026-06-30");
    expect(result.buyer_name).toBe("Atlas Retail Group");
    expect(result.currency).toBe("USD");
    expect(result.subtotal).toBe(2940);
    expect(result.vat_amount).toBe(588);
    expect(result.total_amount).toBe(3528);
    expect(result.line_items).toHaveLength(1);
  });

  it("merges fallback fields without replacing AI-provided values", () => {
    const fallback = fallbackExtractInvoice(invoiceText);
    const merged = mergeWithFallback(
      {
        ...emptyInvoiceExtraction,
        document_type: "invoice",
        supplier_name: "Northstar Print Studio",
        invoice_number: "AI-001",
        confidence_score: 0.82,
        uncertainty_notes: [],
      },
      fallback,
    );

    expect(merged.supplier_name).toBe("Northstar Print Studio");
    expect(merged.invoice_number).toBe("AI-001");
    expect(merged.total_amount).toBe(3528);
    expect(merged.confidence_score).toBe(0.82);
  });
});
