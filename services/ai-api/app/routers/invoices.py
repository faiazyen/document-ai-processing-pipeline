from __future__ import annotations

import uuid
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile, File, Header, HTTPException, Query

from app.config import settings
from app.schemas import (
    InferenceJobAccepted,
    InferenceJobResponse,
    InvoiceExtraction,
    InvoiceResponse,
    InvoiceSummary,
    HealthResponse,
    MetricsResponse,
    ErrorResponse,
    TenantInfo,
    TenantUsageResponse,
)
from app.services import metrics
from app.services.persistence import (
    TenantRecord,
    create_inference_job,
    get_all_invoices,
    get_all_jobs,
    get_database_kind,
    get_invoice_by_id,
    get_job_by_id,
    get_tenant_usage,
    job_to_response,
    record_to_summary,
    tenant_to_info,
)
from app.services.auth import get_tenant_from_api_key
from app.services.pipeline import process_invoice_bytes, run_inference_job

router = APIRouter()

ACCEPTED_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def _validate_upload(file: UploadFile) -> None:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    if file.content_type and file.content_type not in ACCEPTED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Only PDF uploads are accepted.")


async def _read_upload(file: UploadFile) -> bytes:
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 20 MB limit.")
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    return file_bytes


@router.post(
    "/process-invoice",
    response_model=InvoiceResponse,
    summary="Upload and process a PDF invoice",
    description="Accept a PDF file, extract text, run AI and fallback extraction, validate, persist, and return structured invoice data.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file or empty upload"},
        413: {"model": ErrorResponse, "description": "PDF exceeds the upload limit"},
        415: {"model": ErrorResponse, "description": "Unsupported media type"},
        422: {"model": ErrorResponse, "description": "PDF text extraction or request validation failed"},
    },
)
async def process_invoice(file: UploadFile = File(..., description="PDF invoice file")):
    _validate_upload(file)
    file_bytes = await _read_upload(file)
    request_id = str(uuid.uuid4())
    try:
        record, raw_preview = process_invoice_bytes(
            file_bytes=file_bytes,
            filename=file.filename,
            tenant_id=settings.default_tenant_id,
            request_id=request_id,
            region=settings.default_region,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"PDF text extraction failed: {exc}")

    extraction = InvoiceExtraction.model_validate_json(record.extracted_json or "{}")
    return InvoiceResponse(
        id=record.id,
        tenant_id=record.tenant_id,
        request_id=record.request_id,
        filename=file.filename,
        extraction=extraction,
        raw_text_preview=raw_preview,
        created_at=record.created_at.isoformat() if record.created_at else "",
    )


@router.post(
    "/inference/jobs",
    response_model=InferenceJobAccepted,
    summary="Create an async tenant-scoped invoice inference job",
    responses={
        401: {"model": ErrorResponse, "description": "Missing or invalid API key"},
        413: {"model": ErrorResponse, "description": "PDF exceeds the upload limit"},
        415: {"model": ErrorResponse, "description": "Unsupported media type"},
    },
)
async def create_async_inference_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF invoice file"),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    tenant: TenantRecord = Depends(get_tenant_from_api_key),
):
    _validate_upload(file)
    file_bytes = await _read_upload(file)
    request_id = str(uuid.uuid4())
    region = tenant.region_preference or settings.default_region
    job = create_inference_job(
        tenant_id=tenant.id,
        filename=file.filename or "invoice.pdf",
        request_id=request_id,
        region=region,
        idempotency_key=idempotency_key,
    )
    if getattr(job, "_was_created", True) and job.status == "queued":
        background_tasks.add_task(
            run_inference_job,
            job.id,
            file_bytes,
            file.filename or "invoice.pdf",
            tenant.id,
            request_id,
            region,
        )

    return InferenceJobAccepted(
        job_id=job.id,
        tenant_id=job.tenant_id,
        status=job.status,
        request_id=job.request_id,
        region=job.region,
    )


@router.get(
    "/inference/jobs",
    response_model=list[InferenceJobResponse],
    summary="List tenant-scoped inference jobs",
)
def list_inference_jobs(tenant: TenantRecord = Depends(get_tenant_from_api_key)):
    return [job_to_response(job) for job in get_all_jobs(tenant_id=tenant.id)]


@router.get(
    "/inference/jobs/{job_id}",
    response_model=InferenceJobResponse,
    summary="Get a tenant-scoped inference job",
    responses={404: {"model": ErrorResponse, "description": "Inference job not found"}},
)
def get_inference_job(job_id: str, tenant: TenantRecord = Depends(get_tenant_from_api_key)):
    job = get_job_by_id(job_id, tenant_id=tenant.id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Inference job {job_id} not found.")
    return job_to_response(job)


@router.get(
    "/tenants/me",
    response_model=TenantInfo,
    summary="Read authenticated tenant configuration",
)
def get_current_tenant(tenant: TenantRecord = Depends(get_tenant_from_api_key)):
    return tenant_to_info(tenant)


@router.get(
    "/tenants/me/usage",
    response_model=TenantUsageResponse,
    summary="Read authenticated tenant usage and estimated cost",
)
def get_current_tenant_usage(tenant: TenantRecord = Depends(get_tenant_from_api_key)):
    return get_tenant_usage(tenant.id)


@router.get(
    "/invoices",
    response_model=list[InvoiceSummary],
    summary="List processed invoices",
    description="Newest first. Use limit and offset to page through results.",
)
def list_invoices(
    tenant: TenantRecord = Depends(get_tenant_from_api_key),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum results to return"),
    offset: int = Query(default=0, ge=0, description="Results to skip, for pagination"),
):
    records = get_all_invoices(tenant_id=tenant.id, limit=limit, offset=offset)
    return [record_to_summary(r) for r in records]


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get a single processed invoice by ID",
    responses={404: {"model": ErrorResponse, "description": "Invoice not found"}},
)
def get_invoice(invoice_id: int, tenant: TenantRecord = Depends(get_tenant_from_api_key)):
    record = get_invoice_by_id(invoice_id, tenant_id=tenant.id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found.")

    extraction = InvoiceExtraction.model_validate_json(record.extracted_json or "{}")
    return InvoiceResponse(
        id=record.id,
        tenant_id=record.tenant_id,
        request_id=record.request_id,
        filename=record.filename,
        extraction=extraction,
        raw_text_preview=record.raw_text_preview or "",
        created_at=record.created_at.isoformat() if record.created_at else "",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
)
def health():
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        openai_configured=bool(settings.openai_api_key),
        database=get_database_kind(),
    )


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="In-memory processing metrics",
)
def get_metrics():
    return MetricsResponse(**metrics.get_metrics())
