from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class _MetricsStore:
    processed_documents: int = 0
    failed_documents: int = 0
    total_processing_ms: float = 0.0
    fallback_count: int = 0
    validation_warning_count: int = 0
    processing_samples_ms: list[float] = field(default_factory=list)
    llm_samples_ms: list[float] = field(default_factory=list)
    estimated_cost_usd: float = 0.0
    _lock: Lock = field(default_factory=Lock)


_store = _MetricsStore()


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = min(len(sorted_values) - 1, int(round((percentile / 100) * (len(sorted_values) - 1))))
    return sorted_values[index]


def record_success(
    processing_ms: float,
    used_fallback: bool,
    warning_count: int,
    llm_ms: float | None = None,
    estimated_cost_usd: float = 0.0,
) -> None:
    with _store._lock:
        _store.processed_documents += 1
        _store.total_processing_ms += processing_ms
        _store.processing_samples_ms.append(processing_ms)
        if llm_ms is not None:
            _store.llm_samples_ms.append(llm_ms)
        if used_fallback:
            _store.fallback_count += 1
        _store.validation_warning_count += warning_count
        _store.estimated_cost_usd += estimated_cost_usd


def record_failure() -> None:
    with _store._lock:
        _store.failed_documents += 1


def get_metrics() -> dict:
    with _store._lock:
        total = _store.processed_documents
        avg_ms = _store.total_processing_ms / total if total > 0 else 0.0
        fallback_rate = _store.fallback_count / total if total > 0 else 0.0
        return {
            "processed_documents": _store.processed_documents,
            "failed_documents": _store.failed_documents,
            "average_processing_ms": round(avg_ms, 2),
            "p95_processing_ms": round(_percentile(_store.processing_samples_ms, 95), 2),
            "p95_llm_ms": round(_percentile(_store.llm_samples_ms, 95), 2),
            "fallback_rate": round(fallback_rate, 4),
            "validation_warning_count": _store.validation_warning_count,
            "estimated_cost_usd": round(_store.estimated_cost_usd, 8),
        }
