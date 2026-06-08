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
    filename: str
    extraction: InvoiceExtraction
    raw_text_preview: str
    created_at: str


class InvoiceSummary(BaseModel):
    id: int
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


class HealthResponse(BaseModel):
    status: str
    version: str
    openai_configured: bool
    database: str


class MetricsResponse(BaseModel):
    processed_documents: int
    failed_documents: int
    average_processing_ms: float
    fallback_rate: float
    validation_warning_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
