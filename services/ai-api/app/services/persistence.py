from __future__ import annotations

import json
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session
from app.config import settings
from app.schemas import InvoiceExtraction, InvoiceSummary


def _connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def make_engine(database_url: str | None = None) -> Engine:
    url = database_url or settings.database_url
    return create_engine(url, connect_args=_connect_args(url), pool_pre_ping=True)


def get_database_kind(database_url: str | None = None) -> str:
    url = database_url or settings.database_url
    return url.split(":", 1)[0]


engine = make_engine()


class Base(DeclarativeBase):
    pass


class InvoiceRecord(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    document_type = Column(String, nullable=True)
    supplier_name = Column(String, nullable=True)
    buyer_name = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    total_amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    extraction_source = Column(String, nullable=True)
    validation_warnings = Column(Text, nullable=True)  # JSON
    extracted_json = Column(Text, nullable=True)        # JSON
    raw_text_preview = Column(Text, nullable=True)
    processing_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def save_invoice(
    filename: str,
    extraction: InvoiceExtraction,
    raw_text_preview: str,
) -> InvoiceRecord:
    record = InvoiceRecord(
        filename=filename,
        document_type=extraction.document_type,
        supplier_name=extraction.supplier_name,
        buyer_name=extraction.buyer_name,
        invoice_number=extraction.invoice_number,
        total_amount=extraction.total_amount,
        currency=extraction.currency,
        confidence_score=extraction.confidence_score,
        extraction_source=extraction.extraction_source,
        validation_warnings=json.dumps([w.model_dump() for w in extraction.validation_warnings]),
        extracted_json=extraction.model_dump_json(),
        raw_text_preview=raw_text_preview[:1600],
        processing_ms=extraction.processing_ms,
    )
    with Session(engine) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def get_invoice_by_id(invoice_id: int) -> InvoiceRecord | None:
    with Session(engine) as session:
        return session.get(InvoiceRecord, invoice_id)


def get_all_invoices() -> list[InvoiceRecord]:
    with Session(engine) as session:
        return session.query(InvoiceRecord).order_by(InvoiceRecord.id.desc()).all()


def record_to_summary(record: InvoiceRecord) -> InvoiceSummary:
    return InvoiceSummary(
        id=record.id,
        filename=record.filename,
        document_type=record.document_type or "unknown",
        supplier_name=record.supplier_name,
        buyer_name=record.buyer_name,
        invoice_number=record.invoice_number,
        total_amount=record.total_amount,
        currency=record.currency,
        confidence_score=record.confidence_score or 0.0,
        extraction_source=record.extraction_source or "fallback",
        processing_ms=record.processing_ms,
        created_at=record.created_at.isoformat() if record.created_at else "",
    )
