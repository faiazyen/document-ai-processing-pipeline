from app.services.fallback_extract import fallback_extract_invoice


SAMPLE_INVOICE_TEXT = """\
INVOICE

From: Acme Textiles GmbH
Bill To: Merch Maverick Ltd

Invoice Number: INV-2024-042
Invoice Date: 2024-03-15
Due Date: 2024-04-15
Payment Terms: Net 30

Custom Polo Shirts  100  12.00  1200.00

Subtotal: EUR 1200.00
VAT: EUR 240.00
Total Due: EUR 1440.00

Currency: EUR
"""


def test_fallback_extracts_invoice_number():
    result = fallback_extract_invoice(SAMPLE_INVOICE_TEXT)
    assert result.invoice_number is not None
    assert "INV-2024-042" in result.invoice_number


def test_fallback_extracts_invoice_date():
    result = fallback_extract_invoice(SAMPLE_INVOICE_TEXT)
    assert result.invoice_date is not None
    assert "2024" in result.invoice_date


def test_fallback_extracts_currency():
    result = fallback_extract_invoice(SAMPLE_INVOICE_TEXT)
    assert result.currency == "EUR"


def test_fallback_extracts_total_amount():
    result = fallback_extract_invoice(SAMPLE_INVOICE_TEXT)
    assert result.total_amount is not None
    assert result.total_amount > 0


def test_fallback_classifies_as_invoice():
    result = fallback_extract_invoice(SAMPLE_INVOICE_TEXT)
    assert result.document_type == "invoice"


def test_fallback_confidence_below_openai_threshold():
    result = fallback_extract_invoice(SAMPLE_INVOICE_TEXT)
    assert result.confidence_score < 0.74


def test_fallback_returns_unknown_for_non_invoice():
    result = fallback_extract_invoice("Hello, this is a random document with no relevant content.")
    assert result.document_type == "unknown"


def test_fallback_empty_text_returns_empty_extraction():
    result = fallback_extract_invoice("")
    assert result.invoice_number is None
    assert result.total_amount is None
    assert result.document_type == "unknown"
