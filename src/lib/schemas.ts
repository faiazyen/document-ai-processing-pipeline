import { z } from "zod";

export const warningSeveritySchema = z.enum(["low", "medium", "high"]);

export const validationWarningSchema = z.object({
  code: z.string(),
  severity: warningSeveritySchema,
  message: z.string(),
});

export const lineItemSchema = z.object({
  description: z.string().nullable(),
  quantity: z.number().nullable(),
  unit_price: z.number().nullable(),
  total: z.number().nullable(),
});

export const invoiceExtractionSchema = z.object({
  document_type: z.enum(["invoice", "unknown"]),
  supplier_name: z.string().nullable(),
  supplier_country: z.string().nullable(),
  buyer_name: z.string().nullable(),
  invoice_number: z.string().nullable(),
  invoice_date: z.string().nullable(),
  due_date: z.string().nullable(),
  currency: z.string().nullable(),
  subtotal: z.number().nullable(),
  vat_amount: z.number().nullable(),
  total_amount: z.number().nullable(),
  line_items: z.array(lineItemSchema),
  payment_terms: z.string().nullable(),
  confidence_score: z.number().min(0).max(1),
  uncertainty_notes: z.array(z.string()),
});

export const invoiceResponseSchema = z.object({
  success: z.literal(true),
  document_type: z.enum(["invoice", "unknown"]),
  extraction: invoiceExtractionSchema,
  validation_warnings: z.array(validationWarningSchema),
  confidence_score: z.number().min(0).max(1),
  extraction_source: z.enum(["openai", "fallback", "openai_with_fallback"]),
  raw_text_preview: z.string(),
  processing_ms: z.number(),
});

export const errorResponseSchema = z.object({
  success: z.literal(false),
  error: z.string(),
  validation_warnings: z.array(validationWarningSchema),
});

export type ValidationWarning = z.infer<typeof validationWarningSchema>;
export type LineItem = z.infer<typeof lineItemSchema>;
export type InvoiceExtraction = z.infer<typeof invoiceExtractionSchema>;
export type InvoiceProcessResponse = z.infer<typeof invoiceResponseSchema>;
export type InvoiceErrorResponse = z.infer<typeof errorResponseSchema>;

export const emptyInvoiceExtraction: InvoiceExtraction = {
  document_type: "unknown",
  supplier_name: null,
  supplier_country: null,
  buyer_name: null,
  invoice_number: null,
  invoice_date: null,
  due_date: null,
  currency: null,
  subtotal: null,
  vat_amount: null,
  total_amount: null,
  line_items: [],
  payment_terms: null,
  confidence_score: 0,
  uncertainty_notes: [],
};
