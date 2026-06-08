import { describe, expect, it } from "vitest";
import { emptyInvoiceExtraction } from "../src/lib/schemas";
import { validateInvoice } from "../src/lib/validateInvoice";

describe("validateInvoice", () => {
  it("flags missing critical fields", () => {
    const warnings = validateInvoice({
      ...emptyInvoiceExtraction,
      confidence_score: 0.2,
    });

    expect(warnings.map((warning) => warning.code)).toEqual(
      expect.arrayContaining([
        "document_type_uncertain",
        "missing_invoice_number",
        "missing_supplier_name",
        "missing_invoice_date",
        "missing_total_amount",
        "empty_line_items",
        "low_confidence",
      ]),
    );
  });

  it("flags subtotal and tax consistency issues", () => {
    const warnings = validateInvoice({
      ...emptyInvoiceExtraction,
      document_type: "invoice",
      supplier_name: "Northstar Print Studio",
      buyer_name: "Acme Retail Group",
      invoice_number: "INV-100",
      invoice_date: "2026-06-08",
      currency: "USD",
      subtotal: 500,
      vat_amount: 100,
      total_amount: 550,
      confidence_score: 0.9,
      line_items: [
        {
          description: "Screen printed tees",
          quantity: 50,
          unit_price: 10,
          total: 500,
        },
      ],
    });

    expect(warnings.map((warning) => warning.code)).toContain("tax_total_mismatch");
  });

  it("accepts a complete internally consistent invoice", () => {
    const warnings = validateInvoice({
      ...emptyInvoiceExtraction,
      document_type: "invoice",
      supplier_name: "Northstar Print Studio",
      buyer_name: "Acme Retail Group",
      invoice_number: "INV-101",
      invoice_date: "2026-06-08",
      currency: "USD",
      subtotal: 500,
      vat_amount: 100,
      total_amount: 600,
      confidence_score: 0.94,
      line_items: [
        {
          description: "Screen printed tees",
          quantity: 50,
          unit_price: 10,
          total: 500,
        },
      ],
    });

    expect(warnings).toEqual([]);
  });
});
