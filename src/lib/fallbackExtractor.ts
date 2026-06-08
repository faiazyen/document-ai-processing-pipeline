import {
  emptyInvoiceExtraction,
  type InvoiceExtraction,
  type LineItem,
} from "./schemas";

const CURRENCY_SYMBOLS: Record<string, string> = {
  "$": "USD",
  "€": "EUR",
  "£": "GBP",
};

function clean(value: string | undefined) {
  return value?.replace(/\s+/g, " ").trim() || null;
}

function normalizeAmount(value: string | undefined) {
  if (!value) {
    return null;
  }

  const normalized = value.replace(/[^\d.,-]/g, "").replace(/,(?=\d{3}\b)/g, "");
  const decimalSafe = normalized.includes(",") && !normalized.includes(".")
    ? normalized.replace(",", ".")
    : normalized;
  const parsed = Number.parseFloat(decimalSafe);

  return Number.isFinite(parsed) ? parsed : null;
}

function firstMatch(text: string, patterns: RegExp[]) {
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match?.[1]) {
      return clean(match[1]);
    }
  }

  return null;
}

function findCurrency(text: string) {
  const iso = text.match(/\b(USD|EUR|GBP|CAD|AUD|CZK|PLN|CHF|SEK|NOK|DKK)\b/i);
  if (iso?.[1]) {
    return iso[1].toUpperCase();
  }

  const symbol = text.match(/[$€£]/)?.[0];
  return symbol ? CURRENCY_SYMBOLS[symbol] : null;
}

function findAmount(text: string, labels: string[]) {
  const labelPattern = labels.join("|");
  const pattern = new RegExp(
    `^\\s*(?:${labelPattern})\\s*[:#-]?\\s*(?:USD|EUR|GBP|CAD|AUD|CZK|PLN)?\\s*([$€£]?\\s*-?\\d[\\d,.]*)\\s*$`,
    "i",
  );
  const match = text
    .split(/\r?\n/)
    .map((line) => line.match(pattern))
    .find(Boolean);

  return normalizeAmount(match?.[1]);
}

function extractLineItems(text: string): LineItem[] {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  return lines
    .map((line) => {
      const match = line.match(
        /^(.{4,80}?)\s+(\d+(?:[.,]\d+)?)\s+([$€£]?\s?\d[\d,.]*)\s+([$€£]?\s?\d[\d,.]*)$/,
      );

      if (!match) {
        return null;
      }

      return {
        description: clean(match[1]),
        quantity: normalizeAmount(match[2]),
        unit_price: normalizeAmount(match[3]),
        total: normalizeAmount(match[4]),
      } satisfies LineItem;
    })
    .filter((item): item is LineItem => item !== null)
    .slice(0, 12);
}

export function fallbackExtractInvoice(text: string): InvoiceExtraction {
  const invoiceNumber = firstMatch(text, [
    /\binvoice\s*(?:number|no\.?|#)\s*[:#-]?\s*([A-Z0-9][A-Z0-9-_/]+)/i,
    /\binv\s*(?:number|no\.?|#)\s*[:#-]?\s*([A-Z0-9][A-Z0-9-_/]+)/i,
  ]);

  const invoiceDate = firstMatch(text, [
    /\binvoice\s*date\s*[:#-]?\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})/i,
    /\bdate\s*[:#-]?\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})/i,
  ]);

  const dueDate = firstMatch(text, [
    /\bdue\s*date\s*[:#-]?\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})/i,
    /\bpayment\s*due\s*[:#-]?\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})/i,
  ]);

  const supplierName = firstMatch(text, [
    /\bfrom\s*[:#-]?\s*([^\n\r]+)/i,
    /\bsupplier\s*[:#-]?\s*([^\n\r]+)/i,
    /^([A-Z][A-Za-z0-9&.,' -]{3,80})$/m,
  ]);

  const buyerName = firstMatch(text, [
    /\bbill\s*to\s*[:#-]?\s*([^\n\r]+)/i,
    /\bbuyer\s*[:#-]?\s*([^\n\r]+)/i,
    /\bclient\s*[:#-]?\s*([^\n\r]+)/i,
  ]);

  const subtotal = findAmount(text, ["subtotal", "sub total", "net amount"]);
  const vatAmount = findAmount(text, ["vat", "tax", "sales tax"]);
  const totalAmount = findAmount(text, ["grand total", "total due", "balance due", "total"]);
  const paymentTerms = firstMatch(text, [
    /\bpayment\s*terms\s*[:#-]?\s*([^\n\r]+)/i,
    /\bterms\s*[:#-]?\s*([^\n\r]+)/i,
  ]);

  return {
    ...emptyInvoiceExtraction,
    document_type: /invoice/i.test(text) ? "invoice" : "unknown",
    supplier_name: supplierName,
    buyer_name: buyerName,
    invoice_number: invoiceNumber,
    invoice_date: invoiceDate,
    due_date: dueDate,
    currency: findCurrency(text),
    subtotal,
    vat_amount: vatAmount,
    total_amount: totalAmount,
    line_items: extractLineItems(text),
    payment_terms: paymentTerms,
    confidence_score: 0.45,
    uncertainty_notes: ["Rule-based fallback extraction was used."],
  };
}

export function mergeWithFallback(
  primary: InvoiceExtraction,
  fallback: InvoiceExtraction,
): InvoiceExtraction {
  const merged: InvoiceExtraction = {
    ...primary,
    supplier_name: primary.supplier_name || fallback.supplier_name,
    supplier_country: primary.supplier_country || fallback.supplier_country,
    buyer_name: primary.buyer_name || fallback.buyer_name,
    invoice_number: primary.invoice_number || fallback.invoice_number,
    invoice_date: primary.invoice_date || fallback.invoice_date,
    due_date: primary.due_date || fallback.due_date,
    currency: primary.currency || fallback.currency,
    subtotal: primary.subtotal ?? fallback.subtotal,
    vat_amount: primary.vat_amount ?? fallback.vat_amount,
    total_amount: primary.total_amount ?? fallback.total_amount,
    line_items: primary.line_items.length > 0 ? primary.line_items : fallback.line_items,
    payment_terms: primary.payment_terms || fallback.payment_terms,
    confidence_score: Math.max(primary.confidence_score, fallback.confidence_score),
    uncertainty_notes: [
      ...primary.uncertainty_notes,
      "Fallback extractor filled missing critical fields where possible.",
    ],
  };

  if (merged.document_type === "unknown" && fallback.document_type === "invoice") {
    merged.document_type = "invoice";
  }

  return merged;
}
