from __future__ import annotations

import json
import hashlib
import hmac
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session
from app.config import settings
from app.schemas import (
    CostSummary,
    InferenceJobResponse,
    InvoiceExtraction,
    InvoiceSummary,
    JobStatus,
    TenantInfo,
    TenantUsageResponse,
)


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
    tenant_id = Column(String, nullable=True, index=True)
    job_id = Column(String, nullable=True, index=True)
    request_id = Column(String, nullable=True, index=True)
    region = Column(String, nullable=True)
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
    model_name = Column(String, nullable=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TenantRecord(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="active", nullable=False)
    preferred_model = Column(String, nullable=False)
    region_preference = Column(String, nullable=False)
    monthly_request_limit = Column(Integer, nullable=True)
    monthly_cost_limit_usd = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ApiKeyRecord(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    key_hash = Column(String, nullable=False, unique=True, index=True)
    label = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class InferenceJobRecord(Base):
    __tablename__ = "inference_jobs"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default=JobStatus.queued.value, nullable=False, index=True)
    request_id = Column(String, nullable=False, index=True)
    idempotency_key = Column(String, nullable=True, index=True)
    region = Column(String, nullable=False)
    model_name = Column(String, nullable=True)
    raw_text_preview = Column(Text, default="")
    extracted_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    queue_wait_ms = Column(Float, nullable=True)
    processing_ms = Column(Float, nullable=True)
    llm_ms = Column(Float, nullable=True)
    validation_warning_count = Column(Integer, default=0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_invoice_columns()
    ensure_default_tenant()
    ensure_default_api_key()


def _hash_api_key(api_key: str) -> str:
    return hmac.new(
        settings.api_key_hash_secret.encode("utf-8"),
        api_key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def ensure_sqlite_invoice_columns() -> None:
    if get_database_kind() != "sqlite":
        return

    inspector = inspect(engine)
    if "invoices" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("invoices")}
    additions = {
        "tenant_id": "VARCHAR",
        "job_id": "VARCHAR",
        "request_id": "VARCHAR",
        "region": "VARCHAR",
        "model_name": "VARCHAR",
        "input_tokens": "INTEGER DEFAULT 0",
        "output_tokens": "INTEGER DEFAULT 0",
        "total_tokens": "INTEGER DEFAULT 0",
        "estimated_cost_usd": "FLOAT DEFAULT 0.0",
    }
    with engine.begin() as connection:
        for name, column_type in additions.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE invoices ADD COLUMN {name} {column_type}"))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_default_tenant() -> TenantRecord:
    with Session(engine) as session:
        tenant = session.get(TenantRecord, settings.default_tenant_id)
        if tenant is None:
            tenant = TenantRecord(
                id=settings.default_tenant_id,
                name=settings.default_tenant_name,
                status="active",
                preferred_model=settings.openai_model,
                region_preference=settings.default_region,
            )
            session.add(tenant)
            session.commit()
            session.refresh(tenant)
        return tenant


def ensure_default_api_key() -> ApiKeyRecord | None:
    if not settings.platform_dev_api_key:
        return None

    key_hash = _hash_api_key(settings.platform_dev_api_key)
    with Session(engine) as session:
        existing = session.query(ApiKeyRecord).filter(ApiKeyRecord.key_hash == key_hash).first()
        if existing:
            return existing

        record = ApiKeyRecord(
            tenant_id=settings.default_tenant_id,
            key_hash=key_hash,
            label="development",
            active=True,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def create_tenant(
    tenant_id: str,
    name: str,
    status: str = "active",
    preferred_model: str | None = None,
    region_preference: str | None = None,
    monthly_request_limit: int | None = None,
    monthly_cost_limit_usd: float | None = None,
) -> TenantRecord:
    with Session(engine) as session:
        tenant = TenantRecord(
            id=tenant_id,
            name=name,
            status=status,
            preferred_model=preferred_model or settings.openai_model,
            region_preference=region_preference or settings.default_region,
            monthly_request_limit=monthly_request_limit,
            monthly_cost_limit_usd=monthly_cost_limit_usd,
        )
        tenant = session.merge(tenant)
        session.commit()
        session.refresh(tenant)
        return tenant


def create_api_key(tenant_id: str, key_hash: str, label: str = "default") -> ApiKeyRecord:
    with Session(engine) as session:
        record = ApiKeyRecord(tenant_id=tenant_id, key_hash=key_hash, label=label, active=True)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def get_tenant_by_api_key_hash(key_hash: str) -> TenantRecord | None:
    with Session(engine) as session:
        api_key = (
            session.query(ApiKeyRecord)
            .filter(ApiKeyRecord.key_hash == key_hash, ApiKeyRecord.active.is_(True))
            .first()
        )
        if api_key is None:
            return None
        return session.get(TenantRecord, api_key.tenant_id)


def get_tenant_by_id(tenant_id: str) -> TenantRecord | None:
    with Session(engine) as session:
        return session.get(TenantRecord, tenant_id)


def tenant_to_info(tenant: TenantRecord) -> TenantInfo:
    return TenantInfo(
        tenant_id=tenant.id,
        name=tenant.name,
        status=tenant.status,
        preferred_model=tenant.preferred_model,
        region_preference=tenant.region_preference,
        monthly_request_limit=tenant.monthly_request_limit,
        monthly_cost_limit_usd=tenant.monthly_cost_limit_usd,
    )


def save_invoice(
    filename: str,
    extraction: InvoiceExtraction,
    raw_text_preview: str,
    tenant_id: str | None = None,
    job_id: str | None = None,
    request_id: str | None = None,
    region: str | None = None,
    model_name: str | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost_usd: float = 0.0,
) -> InvoiceRecord:
    record = InvoiceRecord(
        tenant_id=tenant_id or settings.default_tenant_id,
        job_id=job_id,
        request_id=request_id,
        region=region or settings.default_region,
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
        model_name=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        estimated_cost_usd=estimated_cost_usd,
    )
    with Session(engine) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def get_invoice_by_id(invoice_id: int, tenant_id: str | None = None) -> InvoiceRecord | None:
    with Session(engine) as session:
        query = session.query(InvoiceRecord).filter(InvoiceRecord.id == invoice_id)
        if tenant_id is not None:
            query = query.filter(InvoiceRecord.tenant_id == tenant_id)
        return query.first()


def get_all_invoices(tenant_id: str | None = None) -> list[InvoiceRecord]:
    with Session(engine) as session:
        query = session.query(InvoiceRecord)
        if tenant_id is not None:
            query = query.filter(InvoiceRecord.tenant_id == tenant_id)
        return query.order_by(InvoiceRecord.id.desc()).all()


def record_to_summary(record: InvoiceRecord) -> InvoiceSummary:
    return InvoiceSummary(
        id=record.id,
        tenant_id=record.tenant_id,
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


def create_inference_job(
    tenant_id: str,
    filename: str,
    request_id: str,
    region: str,
    idempotency_key: str | None = None,
) -> InferenceJobRecord:
    with Session(engine) as session:
        if idempotency_key:
            existing = (
                session.query(InferenceJobRecord)
                .filter(
                    InferenceJobRecord.tenant_id == tenant_id,
                    InferenceJobRecord.idempotency_key == idempotency_key,
                )
                .first()
            )
            if existing:
                existing._was_created = False
                return existing

        job = InferenceJobRecord(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            filename=filename,
            request_id=request_id,
            idempotency_key=idempotency_key,
            region=region,
            status=JobStatus.queued.value,
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        job._was_created = True
        return job


def update_job(job_id: str, **updates) -> InferenceJobRecord | None:
    with Session(engine) as session:
        job = session.get(InferenceJobRecord, job_id)
        if job is None:
            return None
        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)
        job.updated_at = _now()
        session.commit()
        session.refresh(job)
        return job


def get_job_by_id(job_id: str, tenant_id: str | None = None) -> InferenceJobRecord | None:
    with Session(engine) as session:
        query = session.query(InferenceJobRecord).filter(InferenceJobRecord.id == job_id)
        if tenant_id is not None:
            query = query.filter(InferenceJobRecord.tenant_id == tenant_id)
        return query.first()


def get_all_jobs(tenant_id: str | None = None) -> list[InferenceJobRecord]:
    with Session(engine) as session:
        query = session.query(InferenceJobRecord)
        if tenant_id is not None:
            query = query.filter(InferenceJobRecord.tenant_id == tenant_id)
        return query.order_by(InferenceJobRecord.created_at.desc()).all()


def job_to_response(job: InferenceJobRecord) -> InferenceJobResponse:
    extraction = None
    if job.extracted_json:
        extraction = InvoiceExtraction.model_validate_json(job.extracted_json)

    return InferenceJobResponse(
        job_id=job.id,
        tenant_id=job.tenant_id,
        filename=job.filename,
        status=job.status,
        request_id=job.request_id,
        region=job.region,
        idempotency_key=job.idempotency_key,
        extraction=extraction,
        raw_text_preview=job.raw_text_preview or "",
        error_message=job.error_message,
        queue_wait_ms=job.queue_wait_ms,
        processing_ms=job.processing_ms,
        llm_ms=job.llm_ms,
        validation_warning_count=job.validation_warning_count or 0,
        cost=CostSummary(
            model_name=job.model_name,
            input_tokens=job.input_tokens or 0,
            output_tokens=job.output_tokens or 0,
            total_tokens=job.total_tokens or 0,
            estimated_cost_usd=job.estimated_cost_usd or 0.0,
        ),
        created_at=job.created_at.isoformat() if job.created_at else "",
        updated_at=job.updated_at.isoformat() if job.updated_at else "",
    )


def get_tenant_usage(tenant_id: str) -> TenantUsageResponse:
    with Session(engine) as session:
        jobs = session.query(InferenceJobRecord).filter(InferenceJobRecord.tenant_id == tenant_id).all()
        return TenantUsageResponse(
            tenant_id=tenant_id,
            processed_jobs=sum(1 for job in jobs if job.status == JobStatus.succeeded.value),
            failed_jobs=sum(1 for job in jobs if job.status == JobStatus.failed.value),
            total_input_tokens=sum(job.input_tokens or 0 for job in jobs),
            total_output_tokens=sum(job.output_tokens or 0 for job in jobs),
            estimated_cost_usd=round(sum(job.estimated_cost_usd or 0.0 for job in jobs), 8),
        )
