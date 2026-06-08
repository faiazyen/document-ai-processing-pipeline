# Invoice Schema

The canonical extraction shape lives in `src/lib/schemas.ts`.

```json
{
  "document_type": "invoice",
  "supplier_name": "The Merch Maverick",
  "supplier_country": "United States",
  "buyer_name": "Acme Retail Group",
  "invoice_number": "MM-2026-0042",
  "invoice_date": "2026-06-08",
  "due_date": "2026-06-30",
  "currency": "USD",
  "subtotal": 2940,
  "vat_amount": 588,
  "total_amount": 3528,
  "line_items": [
    {
      "description": "Custom Embroidered Hoodies",
      "quantity": 120,
      "unit_price": 24.5,
      "total": 2940
    }
  ],
  "payment_terms": "Net 30",
  "confidence_score": 0.91,
  "uncertainty_notes": []
}
```

## Validation Rules

The deterministic validator warns on:

- unknown document type
- missing invoice number
- missing supplier name
- missing buyer name
- missing invoice date
- missing total amount
- missing or unknown currency
- total lower than subtotal
- subtotal plus VAT/tax mismatch
- empty line items
- confidence below `0.7`

Warnings use:

```json
{
  "code": "missing_invoice_number",
  "severity": "high",
  "message": "Invoice number is missing."
}
```
