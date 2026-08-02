"""Backend smoke tests for demo-app."""

import httpx
import pytest


@pytest.mark.asyncio
async def test_health_endpoint():
    from demo_app.server import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["tool_count"] >= 1


@pytest.mark.asyncio
async def test_tools_endpoint():
    from demo_app.server import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/tools")
        assert resp.status_code == 200
        names = [t["name"] for t in resp.json()["tools"]]
        assert "app_info" in names