import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "database" in data["components"]
        assert "ai_provider" in data["components"]


@pytest.mark.asyncio
async def test_dashboard_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/dashboard")
        assert res.status_code == 200
        data = res.json()
        assert "revenue_at_risk_minor" in data
        assert "revenue_recovered_minor" in data
        assert "recovery_rate_pct" in data
        assert "recovery_timeline" in data


@pytest.mark.asyncio
async def test_recovery_cases_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/recovery/cases?limit=10")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_policies_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/policies")
        assert res.status_code == 200
        data = res.json()
        assert data["approval_threshold_minor"] == 5000000


@pytest.mark.asyncio
async def test_evaluation_benchmark_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/evaluation?dataset_size=100")
        assert res.status_code == 200
        data = res.json()
        assert "revive" in data
        assert "baseline" in data
        assert data["revive"]["revenue_recovered_minor"] >= data["baseline"]["revenue_recovered_minor"]


@pytest.mark.asyncio
async def test_demo_scenarios_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Case A: ₹4,999 -> RECOVERED
        res_a = await client.post("/api/v1/demo/case-a")
        assert res_a.status_code == 200
        data_a = res_a.json()
        assert data_a["recovered"] is True
        assert data_a["status"] == "RECOVERED"

        # Case B: ₹87,000 -> PENDING_APPROVAL
        res_b = await client.post("/api/v1/demo/case-b")
        assert res_b.status_code == 200
        data_b = res_b.json()
        assert data_b["pending_approval"] is True
        assert data_b["status"] == "PENDING_APPROVAL"

        # Case C: Executor failure -> ESCALATED
        res_c = await client.post("/api/v1/demo/case-c")
        assert res_c.status_code == 200
        data_c = res_c.json()
        assert data_c["recovered"] is False
        assert data_c["status"] == "ESCALATED"
