from __future__ import annotations

import re
from app.schemas import InvoiceExtraction, LineItem

CURRENCY_SYMBOLS: dict[str, str] = {"$": "USD", "€": "EUR", "£": "GBP"}


def _clean(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = " ".join(value.split()).strip()
    return cleaned or None


def _normalize_amount(value: str | None) -> float | None:
    if not value:
        return None
    normalized = re.sub(r"[^\d.,-]", "", value)
    # European comma-as-decimal: "1.234,56" or "1234,56"
    if "," in normalized and "." not in normalized:
        normalized = normalized.replace(",", ".")
    else:
        # Strip thousand separators
        normalized = re.sub(r",(?=\d{3}\b)", "", normalized)
    try:
        result = float(normalized)
        return result if result == result else None  # NaN guard
    except ValueError:
        return None


def _first_match(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match and match.group(1):
            return _clean(match.group(1))
    return None


def _find_currency(text: str) -> str | None:
    iso = re.search(r"\b(USD|EUR|GBP|CAD|AUD|CZK|PLN|CHF|SEK|NOK|DKK)\b", text, re.IGNORECASE)
    if iso:
        return iso.group(1).upper()
    symbol = re.search(r"[$€£]", text)
    if symbol:
        return CURRENCY_SYMBOLS.get(symbol.group(0))
    return None


def _find_amount(text: str, labels: list[str]) -> float | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = (
        rf"^\s*(?:{label_pattern})\s*[:#-]?\s*"
        rf"(?:USD|EUR|GBP|CAD|AUD|CZK|PLN)?\s*"
        rf"([$€£]?\s*-?\d[\d,.]*).*$"
    )
    for line in text.splitlines():
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            return _normalize_amount(match.group(1))
    return None


def _extract_line_items(text: str) -> list[LineItem]:
    items: list[LineItem] = []
    for line in text.splitlines():
        line = line.strip()
        match = re.match(
            r"^(.{4,80}?)\s+(\d+(?:[.,]\d+)?)\s+([$€£]?\s?\d[\d,.]*)\s+([$€£]?\s?\d[\d,.]*)$",
            line,
        )
        if match:
            items.append(LineItem(
                description=_clean(match.group(1)),
                quantity=_normalize_amount(match.group(2)),
                unit_price=_normalize_amount(match.group(3)),
                total=_normalize_amount(match.group(4)),
            ))
            if len(items) >= 12:
                break
    return items


def fallback_extract_invoice(text: str) -> InvoiceExtraction:
    invoice_number = _first_match(text, [
        r"\binvoice\s*(?:number|no\.?|#)\s*[:#-]?\s*([A-Z0-9][A-Z0-9\-_/]+)",
        r"\binv\s*(?:number|no\.?|#)\s*[:#-]?\s*([A-Z0-9][A-Z0-9\-_/]+)",
    ])
    invoice_date = _first_match(text, [
        r"\binvoice\s*date\s*[:#-]?\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
        r"\bdate\s*[:#-]?\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
    ])
    due_date = _first_match(text, [
        r"\bdue\s*date\s*[:#-]?\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
        r"\bpayment\s*due\s*[:#-]?\s*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})",
    ])
    supplier_name = _first_match(text, [
        r"\bfrom\s*[:#-]?\s*([^\n\r]+)",
        r"\bsupplier\s*[:#-]?\s*([^\n\r]+)",
    ])
    buyer_name = _first_match(text, [
        r"\bbill\s*to\s*[:#-]?\s*([^\n\r]+)",
        r"\bbuyer\s*[:#-]?\s*([^\n\r]+)",
        r"\bclient\s*[:#-]?\s*([^\n\r]+)",
    ])
    subtotal = _find_amount(text, ["subtotal", "sub total", "net amount"])
    vat_amount = _find_amount(text, ["vat", "tax", "sales tax"])
    total_amount = _find_amount(text, ["grand total", "total due", "balance due", "total"])
    payment_terms = _first_match(text, [
        r"\bpayment\s*terms\s*[:#-]?\s*([^\n\r]+)",
        r"\bterms\s*[:#-]?\s*([^\n\r]+)",
    ])
    doc_type = "invoice" if re.search(r"\binvoice\b", text, re.IGNORECASE) else "unknown"

    return InvoiceExtraction(
        document_type=doc_type,
        supplier_name=supplier_name,
        buyer_name=buyer_name,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        currency=_find_currency(text),
        subtotal=subtotal,
        vat_amount=vat_amount,
        total_amount=total_amount,
        line_items=_extract_line_items(text),
        payment_terms=payment_terms,
        confidence_score=0.45,
        extraction_source="fallback",
    )


def merge_with_fallback(primary: InvoiceExtraction, fallback: InvoiceExtraction) -> InvoiceExtraction:
    return InvoiceExtraction(
        document_type=primary.document_type if primary.document_type == "invoice" else fallback.document_type,
        supplier_name=primary.supplier_name or fallback.supplier_name,
        supplier_country=primary.supplier_country or fallback.supplier_country,
        buyer_name=primary.buyer_name or fallback.buyer_name,
        invoice_number=primary.invoice_number or fallback.invoice_number,
        invoice_date=primary.invoice_date or fallback.invoice_date,
        due_date=primary.due_date or fallback.due_date,
        currency=primary.currency or fallback.currency,
        subtotal=primary.subtotal if primary.subtotal is not None else fallback.subtotal,
        vat_amount=primary.vat_amount if primary.vat_amount is not None else fallback.vat_amount,
        total_amount=primary.total_amount if primary.total_amount is not None else fallback.total_amount,
        line_items=primary.line_items if primary.line_items else fallback.line_items,
        payment_terms=primary.payment_terms or fallback.payment_terms,
        confidence_score=max(primary.confidence_score, fallback.confidence_score),
        extraction_source="openai_with_fallback",
    )
