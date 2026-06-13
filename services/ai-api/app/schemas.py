from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ExtractionSource(str, Enum):
    openai = "openai"
    fallback = "fallback"
    openai_with_fallback = "openai_with_fallback"
    hybrid = "hybrid"


class WarningSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TenantStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    succeeded = "succeeded"
    failed = "failed"
    retrying = "retrying"
    dead_lettered = "dead_lettered"


class ValidationWarning(BaseModel):
    code: str
    severity: WarningSeverity
    message: str


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


class InvoiceExtraction(BaseModel):
    document_type: str = "invoice"
    supplier_name: Optional[str] = None
    supplier_country: Optional[str] = None
    buyer_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    vat_amount: Optional[float] = None
    total_amount: Optional[float] = None
    line_items: list[LineItem] = Field(default_factory=list)
    payment_terms: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    validation_warnings: list[ValidationWarning] = Field(default_factory=list)
    extraction_source: ExtractionSource = ExtractionSource.fallback
    processing_ms: Optional[float] = None


class InvoiceResponse(BaseModel):
    id: int
    tenant_id: Optional[str] = None
    request_id: Optional[str] = None
    filename: str
    extraction: InvoiceExtraction
    raw_text_preview: str
    created_at: str


class InvoiceSummary(BaseModel):
    id: int
    tenant_id: Optional[str] = None
    filename: str
    document_type: str
    supplier_name: Optional[str]
    buyer_name: Optional[str]
    invoice_number: Optional[str]
    total_amount: Optional[float]
    currency: Optional[str]
    confidence_score: float
    extraction_source: str
    processing_ms: Optional[float]
    created_at: str


class TenantInfo(BaseModel):
    tenant_id: str
    name: str
    status: TenantStatus
    preferred_model: str
    region_preference: str
    monthly_request_limit: Optional[int] = None
    monthly_cost_limit_usd: Optional[float] = None


class InferenceJobAccepted(BaseModel):
    job_id: str
    tenant_id: str
    status: JobStatus
    request_id: str
    region: str


class CostSummary(BaseModel):
    model_name: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class InferenceJobResponse(BaseModel):
    job_id: str
    tenant_id: str
    filename: str
    status: JobStatus
    request_id: str
    region: str
    idempotency_key: Optional[str] = None
    extraction: Optional[InvoiceExtraction] = None
    raw_text_preview: str = ""
    error_message: Optional[str] = None
    queue_wait_ms: Optional[float] = None
    processing_ms: Optional[float] = None
    llm_ms: Optional[float] = None
    validation_warning_count: int = 0
    cost: CostSummary = Field(default_factory=CostSummary)
    created_at: str
    updated_at: str


class TenantUsageResponse(BaseModel):
    tenant_id: str
    processed_jobs: int
    failed_jobs: int
    total_input_tokens: int
    total_output_tokens: int
    estimated_cost_usd: float


class HealthResponse(BaseModel):
    status: str
    version: str
    openai_configured: bool
    database: str


class MetricsResponse(BaseModel):
    processed_documents: int
    failed_documents: int
    average_processing_ms: float
    p95_processing_ms: float = 0.0
    p95_llm_ms: float = 0.0
    fallback_rate: float
    validation_warning_count: int
    estimated_cost_usd: float = 0.0


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
