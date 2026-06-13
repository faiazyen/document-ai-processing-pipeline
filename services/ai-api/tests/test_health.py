import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.anyio
async def test_health_returns_ok():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "openai_configured" in data
    assert data["database"] == "sqlite"


@pytest.mark.anyio
async def test_metrics_returns_expected_shape():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    expected_keys = {
        "processed_documents",
        "failed_documents",
        "average_processing_ms",
        "p95_processing_ms",
        "p95_llm_ms",
        "fallback_rate",
        "validation_warning_count",
        "estimated_cost_usd",
    }
    assert expected_keys.issubset(data.keys())
    assert isinstance(data["processed_documents"], int)
    assert isinstance(data["fallback_rate"], float)
