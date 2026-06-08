import type { InvoiceExtraction, ValidationWarning } from "./schemas";

const KNOWN_CURRENCIES = new Set([
  "USD",
  "EUR",
  "GBP",
  "CAD",
  "AUD",
  "CZK",
  "PLN",
  "SEK",
  "NOK",
  "DKK",
  "CHF",
]);

function isBlank(value: string | null | undefined) {
  return !value || value.trim().length === 0;
}

function moneyClose(left: number, right: number) {
  return Math.abs(left - right) <= 0.02;
}

function warning(
  code: string,
  severity: ValidationWarning["severity"],
  message: string,
): ValidationWarning {
  return { code, severity, message };
}

export function validateInvoice(invoice: InvoiceExtraction): ValidationWarning[] {
  const warnings: ValidationWarning[] = [];

  if (invoice.document_type !== "invoice") {
    warnings.push(
      warning(
        "document_type_uncertain",
        "high",
        "Document type was not confidently classified as an invoice.",
      ),
    );
  }

  if (isBlank(invoice.invoice_number)) {
    warnings.push(
      warning("missing_invoice_number", "high", "Invoice number is missing."),
    );
  }

  if (isBlank(invoice.supplier_name)) {
    warnings.push(
      warning("missing_supplier_name", "high", "Supplier name is missing."),
    );
  }

  if (isBlank(invoice.buyer_name)) {
    warnings.push(warning("missing_buyer_name", "medium", "Buyer name is missing."));
  }

  if (isBlank(invoice.invoice_date)) {
    warnings.push(
      warning("missing_invoice_date", "high", "Invoice date is missing."),
    );
  }

  if (invoice.total_amount === null) {
    warnings.push(
      warning("missing_total_amount", "high", "Total amount is missing."),
    );
  }

  if (invoice.currency === null || isBlank(invoice.currency)) {
    warnings.push(warning("missing_currency", "medium", "Currency is missing."));
  } else if (!KNOWN_CURRENCIES.has(invoice.currency.toUpperCase())) {
    warnings.push(
      warning(
        "unknown_currency",
        "medium",
        `Currency "${invoice.currency}" is not in the recognized currency set.`,
      ),
    );
  }

  if (invoice.subtotal !== null && invoice.total_amount !== null) {
    if (invoice.total_amount < invoice.subtotal) {
      warnings.push(
        warning(
          "total_lower_than_subtotal",
          "high",
          "Total amount is lower than subtotal.",
        ),
      );
    }
  }

  if (
    invoice.subtotal !== null &&
    invoice.vat_amount !== null &&
    invoice.total_amount !== null
  ) {
    const expected = invoice.subtotal + invoice.vat_amount;
    if (!moneyClose(invoice.total_amount, expected)) {
      warnings.push(
        warning(
          "tax_total_mismatch",
          "high",
          "Total amount does not match subtotal plus VAT/tax.",
        ),
      );
    }
  }

  if (invoice.line_items.length === 0) {
    warnings.push(
      warning("empty_line_items", "medium", "No invoice line items were extracted."),
    );
  }

  if (invoice.confidence_score < 0.7) {
    warnings.push(
      warning(
        "low_confidence",
        "medium",
        "Extraction confidence is below the review threshold.",
      ),
    );
  }

  return warnings;
}
