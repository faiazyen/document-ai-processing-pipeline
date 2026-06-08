from __future__ import annotations

from app.schemas import InvoiceExtraction, ValidationWarning, WarningSeverity

KNOWN_CURRENCIES = {
    "USD", "EUR", "GBP", "CAD", "AUD", "CZK", "PLN", "SEK", "NOK", "DKK", "CHF",
}


def _warn(code: str, severity: WarningSeverity, message: str) -> ValidationWarning:
    return ValidationWarning(code=code, severity=severity, message=message)


def _blank(value: str | None) -> bool:
    return not value or not value.strip()


def validate_invoice(extraction: InvoiceExtraction) -> list[ValidationWarning]:
    warnings: list[ValidationWarning] = []

    if extraction.document_type not in ("invoice",):
        warnings.append(_warn(
            "document_type_uncertain", WarningSeverity.high,
            "Document type was not confidently classified as an invoice.",
        ))

    if _blank(extraction.invoice_number):
        warnings.append(_warn("missing_invoice_number", WarningSeverity.high, "Invoice number is missing."))

    if _blank(extraction.supplier_name):
        warnings.append(_warn("missing_supplier_name", WarningSeverity.high, "Supplier name is missing."))

    if _blank(extraction.buyer_name):
        warnings.append(_warn("missing_buyer_name", WarningSeverity.medium, "Buyer name is missing."))

    if _blank(extraction.invoice_date):
        warnings.append(_warn("missing_invoice_date", WarningSeverity.high, "Invoice date is missing."))

    if extraction.total_amount is None:
        warnings.append(_warn("missing_total_amount", WarningSeverity.high, "Total amount is missing."))

    if _blank(extraction.currency):
        warnings.append(_warn("missing_currency", WarningSeverity.medium, "Currency is missing."))
    elif extraction.currency.upper() not in KNOWN_CURRENCIES:
        warnings.append(_warn(
            "unknown_currency", WarningSeverity.medium,
            f'Currency "{extraction.currency}" is not in the recognized set.',
        ))

    if extraction.subtotal is not None and extraction.total_amount is not None:
        if extraction.total_amount < extraction.subtotal:
            warnings.append(_warn(
                "total_lower_than_subtotal", WarningSeverity.high,
                "Total amount is lower than subtotal.",
            ))

    if (
        extraction.subtotal is not None
        and extraction.vat_amount is not None
        and extraction.total_amount is not None
    ):
        expected = extraction.subtotal + extraction.vat_amount
        if abs(extraction.total_amount - expected) > 0.02:
            warnings.append(_warn(
                "tax_total_mismatch", WarningSeverity.high,
                "Total amount does not match subtotal + VAT.",
            ))

    if not extraction.line_items:
        warnings.append(_warn("empty_line_items", WarningSeverity.medium, "No line items were extracted."))

    if extraction.confidence_score < 0.7:
        warnings.append(_warn(
            "low_confidence", WarningSeverity.medium,
            "Extraction confidence is below the review threshold (0.70).",
        ))

    return warnings
