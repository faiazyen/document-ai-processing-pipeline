from __future__ import annotations

import time

from app.config import settings
from app.schemas import InvoiceExtraction, JobStatus, ValidationWarning
from app.services import metrics, persistence
from app.services.costing import estimate_openai_cost_usd, estimate_tokens
from app.services.extract_text import extract_text_from_pdf, is_scanned_pdf
from app.services.fallback_extract import fallback_extract_invoice, merge_with_fallback
from app.services.validate_invoice import validate_invoice


CRITICAL_WARNING_CODES = {
    "missing_invoice_number",
    "missing_supplier_name",
    "missing_invoice_date",
    "missing_total_amount",
}


def should_use_fallback(warning_codes: list[str], confidence: float) -> bool:
    return confidence < 0.74 or bool(CRITICAL_WARNING_CODES & set(warning_codes))


def process_invoice_bytes(
    file_bytes: bytes,
    filename: str,
    tenant_id: str,
    request_id: str,
    region: str,
    job_id: str | None = None,
) -> tuple[persistence.InvoiceRecord, str]:
    started_at = time.monotonic()
    llm_ms: float | None = None

    text = extract_text_from_pdf(file_bytes)
    scanned = is_scanned_pdf(text)
    fallback = fallback_extract_invoice(text)
    extraction: InvoiceExtraction = fallback
    model_name: str | None = None
    input_tokens = 0
    output_tokens = 0
    estimated_cost_usd = 0.0

    if scanned:
        extraction.validation_warnings.append(
            ValidationWarning(
                code="scanned_pdf_requires_ocr",
                severity="high",
                message=(
                    "This PDF appears to be image-only with no extractable text. "
                    "Production deployments should route through an OCR service "
                    "before structured extraction."
                ),
            )
        )
    else:
        try:
            from app.services.openai_extract import extract_invoice_with_openai

            llm_started_at = time.monotonic()
            openai_result = extract_invoice_with_openai(text)
            llm_ms = round((time.monotonic() - llm_started_at) * 1000, 2)
            model_name = settings.openai_model
            input_tokens = estimate_tokens(text[:6000])
            output_tokens = estimate_tokens(openai_result.model_dump_json())
            estimated_cost_usd = estimate_openai_cost_usd(input_tokens, output_tokens)

            initial_warnings = validate_invoice(openai_result)
            warning_codes = [warning.code for warning in initial_warnings]

            if should_use_fallback(warning_codes, openai_result.confidence_score):
                extraction = merge_with_fallback(openai_result, fallback)
            else:
                extraction = openai_result
        except Exception:
            extraction = fallback

    validation_warnings = validate_invoice(extraction)
    extraction.validation_warnings = validation_warnings
    extraction.processing_ms = round((time.monotonic() - started_at) * 1000, 2)

    used_fallback = extraction.extraction_source in ("fallback", "openai_with_fallback")
    metrics.record_success(
        processing_ms=extraction.processing_ms,
        used_fallback=used_fallback,
        warning_count=len(validation_warnings),
        llm_ms=llm_ms,
        estimated_cost_usd=estimated_cost_usd,
    )

    raw_preview = text[:1600]
    record = persistence.save_invoice(
        filename=filename,
        extraction=extraction,
        raw_text_preview=raw_preview,
        tenant_id=tenant_id,
        job_id=job_id,
        request_id=request_id,
        region=region,
        model_name=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimated_cost_usd,
    )

    if job_id:
        persistence.update_job(
            job_id,
            status=JobStatus.succeeded.value,
            raw_text_preview=raw_preview,
            extracted_json=extraction.model_dump_json(),
            queue_wait_ms=0.0,
            processing_ms=extraction.processing_ms,
            llm_ms=llm_ms,
            validation_warning_count=len(validation_warnings),
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost_usd=estimated_cost_usd,
            error_message=None,
        )

    return record, raw_preview


def run_inference_job(
    job_id: str,
    file_bytes: bytes,
    filename: str,
    tenant_id: str,
    request_id: str,
    region: str,
) -> None:
    persistence.update_job(job_id, status=JobStatus.processing.value)
    try:
        process_invoice_bytes(
            file_bytes=file_bytes,
            filename=filename,
            tenant_id=tenant_id,
            request_id=request_id,
            region=region,
            job_id=job_id,
        )
    except Exception as exc:
        metrics.record_failure()
        persistence.update_job(
            job_id,
            status=JobStatus.failed.value,
            error_message=str(exc),
        )
