import pytest
from app.schemas import InvoiceExtraction, LineItem
from app.services.validate_invoice import validate_invoice


def _base_invoice(**kwargs) -> InvoiceExtraction:
    defaults = dict(
        document_type="invoice",
        supplier_name="Acme Textiles",
        buyer_name="Merch Maverick Ltd",
        invoice_number="INV-2024-001",
        invoice_date="2024-01-15",
        total_amount=1200.00,
        currency="EUR",
        confidence_score=0.92,
        extraction_source="openai",
        line_items=[LineItem(description="Custom T-Shirts", quantity=100, unit_price=12.0, total=1200.0)],
    )
    defaults.update(kwargs)
    return InvoiceExtraction(**defaults)


def test_valid_invoice_produces_no_critical_warnings():
    warnings = validate_invoice(_base_invoice())
    high = [w for w in warnings if w.severity == "high"]
    assert high == [], f"Unexpected high warnings: {high}"


def test_missing_invoice_number_raises_high_warning():
    warnings = validate_invoice(_base_invoice(invoice_number=None))
    codes = [w.code for w in warnings]
    assert "missing_invoice_number" in codes


def test_missing_supplier_name_raises_high_warning():
    warnings = validate_invoice(_base_invoice(supplier_name=None))
    codes = [w.code for w in warnings]
    assert "missing_supplier_name" in codes


def test_missing_total_raises_high_warning():
    warnings = validate_invoice(_base_invoice(total_amount=None))
    codes = [w.code for w in warnings]
    assert "missing_total_amount" in codes


def test_unknown_currency_raises_medium_warning():
    warnings = validate_invoice(_base_invoice(currency="XYZ"))
    codes = [w.code for w in warnings]
    assert "unknown_currency" in codes


def test_total_lower_than_subtotal_raises_high_warning():
    warnings = validate_invoice(_base_invoice(subtotal=1500.0, total_amount=1000.0))
    codes = [w.code for w in warnings]
    assert "total_lower_than_subtotal" in codes


def test_tax_mismatch_raises_high_warning():
    warnings = validate_invoice(_base_invoice(subtotal=1000.0, vat_amount=200.0, total_amount=1100.0))
    codes = [w.code for w in warnings]
    assert "tax_total_mismatch" in codes


def test_empty_line_items_raises_medium_warning():
    warnings = validate_invoice(_base_invoice(line_items=[]))
    codes = [w.code for w in warnings]
    assert "empty_line_items" in codes


def test_low_confidence_raises_medium_warning():
    warnings = validate_invoice(_base_invoice(confidence_score=0.5))
    codes = [w.code for w in warnings]
    assert "low_confidence" in codes


def test_valid_subtotal_plus_vat_equals_total_no_mismatch():
    warnings = validate_invoice(_base_invoice(subtotal=1000.0, vat_amount=200.0, total_amount=1200.0))
    codes = [w.code for w in warnings]
    assert "tax_total_mismatch" not in codes
