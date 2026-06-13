import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_openapi_documents_core_invoice_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/process-invoice" in paths
    assert "/inference/jobs" in paths
    assert "/inference/jobs/{job_id}" in paths
    assert "/tenants/me" in paths
    assert "/tenants/me/usage" in paths
    assert "/invoices" in paths
    assert "/invoices/{invoice_id}" in paths
    assert "/health" in paths
    assert "/metrics" in paths
    assert "415" in paths["/process-invoice"]["post"]["responses"]
    assert "401" in paths["/inference/jobs"]["post"]["responses"]


@pytest.mark.anyio
async def test_invalid_upload_returns_consistent_error_shape():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/process-invoice",
            files={"file": ("not-an-invoice.txt", b"hello", "text/plain")},
        )

    assert response.status_code == 400
    assert response.json() == {
        "error": "Only PDF files are accepted.",
        "detail": None,
    }


@pytest.mark.anyio
async def test_wrong_content_type_for_pdf_name_is_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/process-invoice",
            files={"file": ("invoice.pdf", b"hello", "text/plain")},
        )

    assert response.status_code == 415
    assert response.json()["error"] == "Only PDF uploads are accepted."
