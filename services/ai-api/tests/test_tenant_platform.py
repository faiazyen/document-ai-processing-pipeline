import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.schemas import InvoiceExtraction, JobStatus
from app.services import persistence
from app.services.auth import hash_api_key

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    test_engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(persistence, "engine", test_engine)
    persistence.Base.metadata.create_all(bind=test_engine)
    persistence.create_tenant("tenant-a", "Tenant A", region_preference="eu-local")
    persistence.create_tenant("tenant-b", "Tenant B", region_preference="us-local")
    persistence.create_api_key("tenant-a", hash_api_key("tenant-a-key"))
    persistence.create_api_key("tenant-b", hash_api_key("tenant-b-key"))
    yield
    persistence.Base.metadata.drop_all(bind=test_engine)


def _sample_extraction(invoice_number: str) -> InvoiceExtraction:
    return InvoiceExtraction(
        document_type="invoice",
        supplier_name="Northstar Print Studio",
        buyer_name="Atlas Retail Group",
        invoice_number=invoice_number,
        invoice_date="2026-06-08",
        total_amount=3528.0,
        currency="USD",
        confidence_score=0.88,
        extraction_source="fallback",
    )


@pytest.mark.anyio
async def test_tenant_me_requires_api_key():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tenants/me")

    assert response.status_code == 401
    assert response.json()["error"] == "Missing X-API-Key header."


@pytest.mark.anyio
async def test_tenant_me_returns_authenticated_tenant():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/tenants/me", headers={"X-API-Key": "tenant-a-key"})

    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == "tenant-a"
    assert data["region_preference"] == "eu-local"


@pytest.mark.anyio
async def test_invoice_listing_is_tenant_scoped():
    persistence.save_invoice(
        "a.pdf",
        _sample_extraction("A-001"),
        "raw text",
        tenant_id="tenant-a",
        request_id="req-a",
    )
    persistence.save_invoice(
        "b.pdf",
        _sample_extraction("B-001"),
        "raw text",
        tenant_id="tenant-b",
        request_id="req-b",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/invoices", headers={"X-API-Key": "tenant-a-key"})

    assert response.status_code == 200
    invoices = response.json()
    assert len(invoices) == 1
    assert invoices[0]["tenant_id"] == "tenant-a"
    assert invoices[0]["invoice_number"] == "A-001"


@pytest.mark.anyio
async def test_cross_tenant_invoice_read_is_blocked():
    record = persistence.save_invoice(
        "b.pdf",
        _sample_extraction("B-001"),
        "raw text",
        tenant_id="tenant-b",
        request_id="req-b",
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/invoices/{record.id}",
            headers={"X-API-Key": "tenant-a-key"},
        )

    assert response.status_code == 404


def test_tenant_usage_aggregates_job_costs():
    job = persistence.create_inference_job(
        tenant_id="tenant-a",
        filename="invoice.pdf",
        request_id="req-1",
        region="eu-local",
    )
    persistence.update_job(
        job.id,
        status=JobStatus.succeeded.value,
        input_tokens=1000,
        output_tokens=250,
        total_tokens=1250,
        estimated_cost_usd=0.0042,
    )

    usage = persistence.get_tenant_usage("tenant-a")

    assert usage.processed_jobs == 1
    assert usage.failed_jobs == 0
    assert usage.total_input_tokens == 1000
    assert usage.total_output_tokens == 250
    assert usage.estimated_cost_usd == 0.0042
