from __future__ import annotations

import time
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.schemas import (
    InvoiceExtraction,
    InvoiceResponse,
    InvoiceSummary,
    HealthResponse,
    MetricsResponse,
    ErrorResponse,
    ValidationWarning,
)
from app.services.extract_text import extract_text_from_pdf, is_scanned_pdf
from app.services.fallback_extract import fallback_extract_invoice, merge_with_fallback
from app.services.validate_invoice import validate_invoice
from app.services.persistence import (
    get_all_invoices,
    get_database_kind,
    get_invoice_by_id,
    record_to_summary,
    save_invoice,
)
from app.services import metrics

router = APIRouter()

ACCEPTED_CONTENT_TYPES = {"application/pdf", "application/octet-stream"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def _should_use_fallback(warning_codes: list[str], confidence: float) -> bool:
    critical = {"missing_invoice_number", "missing_supplier_name", "missing_invoice_date", "missing_total_amount"}
    return confidence < 0.74 or bool(critical & set(warning_codes))


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
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    if file.content_type and file.content_type not in ACCEPTED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Only PDF uploads are accepted.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 20 MB limit.")
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    started_at = time.monotonic()

    try:
        text = extract_text_from_pdf(file_bytes)
    except Exception as exc:
        metrics.record_failure()
        raise HTTPException(status_code=422, detail=f"PDF text extraction failed: {exc}")

    scanned = is_scanned_pdf(text)
    fallback = fallback_extract_invoice(text)

    extraction: InvoiceExtraction = fallback

    if scanned:
        extraction.validation_warnings.append(
            ValidationWarning(
                code="scanned_pdf_requires_ocr",
                severity="high",
                message=(
                    "This PDF appears to be image-only with no extractable text. "
                    "Production deployments should route through an OCR service "
                    "(AWS Textract / Azure Document Intelligence / Google Document AI)."
                ),
            )
        )
    else:
        try:
            from app.services.openai_extract import extract_invoice_with_openai
            openai_result = extract_invoice_with_openai(text)
            initial_warnings = validate_invoice(openai_result)
            warning_codes = [w.code for w in initial_warnings]

            if _should_use_fallback(warning_codes, openai_result.confidence_score):
                extraction = merge_with_fallback(openai_result, fallback)
            else:
                extraction = openai_result
        except Exception:
            # OpenAI unavailable or key missing — fall through to pure fallback
            pass

    validation_warnings = validate_invoice(extraction)
    extraction.validation_warnings = validation_warnings
    extraction.processing_ms = round((time.monotonic() - started_at) * 1000, 2)

    used_fallback = extraction.extraction_source in ("fallback", "openai_with_fallback")
    metrics.record_success(
        processing_ms=extraction.processing_ms,
        used_fallback=used_fallback,
        warning_count=len(validation_warnings),
    )

    raw_preview = text[:1600]

    try:
        record = save_invoice(
            filename=file.filename,
            extraction=extraction,
            raw_text_preview=raw_preview,
        )
        record_id = record.id
        created_at = record.created_at.isoformat() if record.created_at else ""
    except Exception:
        # Persist failure must never crash the API response
        record_id = -1
        created_at = ""

    return InvoiceResponse(
        id=record_id,
        filename=file.filename,
        extraction=extraction,
        raw_text_preview=raw_preview,
        created_at=created_at,
    )


@router.get(
    "/invoices",
    response_model=list[InvoiceSummary],
    summary="List processed invoices",
)
def list_invoices():
    records = get_all_invoices()
    return [record_to_summary(r) for r in records]


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get a single processed invoice by ID",
    responses={404: {"model": ErrorResponse, "description": "Invoice not found"}},
)
def get_invoice(invoice_id: int):
    record = get_invoice_by_id(invoice_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found.")

    extraction = InvoiceExtraction.model_validate_json(record.extracted_json or "{}")
    return InvoiceResponse(
        id=record.id,
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
