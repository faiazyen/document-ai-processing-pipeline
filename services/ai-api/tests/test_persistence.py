import pytest
import os
from sqlalchemy import create_engine
from app.schemas import InvoiceExtraction
from app.services import persistence

# Override to in-memory SQLite for tests
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    monkeypatch.setattr(persistence, "engine", test_engine)
    persistence.Base.metadata.create_all(bind=test_engine)
    yield
    persistence.Base.metadata.drop_all(bind=test_engine)


def _sample_extraction(**kwargs) -> InvoiceExtraction:
    defaults = dict(
        document_type="invoice",
        supplier_name="Acme Textiles",
        buyer_name="Merch Maverick Ltd",
        invoice_number="INV-001",
        invoice_date="2024-01-15",
        total_amount=1200.0,
        currency="EUR",
        confidence_score=0.88,
        extraction_source="openai",
    )
    defaults.update(kwargs)
    return InvoiceExtraction(**defaults)


def test_save_and_retrieve_invoice():
    extraction = _sample_extraction()
    record = persistence.save_invoice("test.pdf", extraction, "raw preview text")
    assert record.id is not None
    assert record.id > 0
    fetched = persistence.get_invoice_by_id(record.id)
    assert fetched is not None
    assert fetched.supplier_name == "Acme Textiles"
    assert fetched.invoice_number == "INV-001"


def test_list_invoices_returns_all():
    persistence.save_invoice("a.pdf", _sample_extraction(invoice_number="INV-001"), "")
    persistence.save_invoice("b.pdf", _sample_extraction(invoice_number="INV-002"), "")
    records = persistence.get_all_invoices()
    assert len(records) == 2


def test_get_nonexistent_invoice_returns_none():
    result = persistence.get_invoice_by_id(99999)
    assert result is None


def test_record_to_summary_shape():
    record = persistence.save_invoice("test.pdf", _sample_extraction(), "preview")
    summary = persistence.record_to_summary(record)
    assert summary.id == record.id
    assert summary.filename == "test.pdf"
    assert summary.currency == "EUR"
