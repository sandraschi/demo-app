"""FastMCP 3.4 server with FastAPI HTTP app for demo-app.

Run: uv run uvicorn demo_app.server:app --host 127.0.0.1 --port 11140
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import Context, FastMCP

from . import db as _db

_db.init_db()
_db.seed_products()

mcp = FastMCP(
    "demo-app",
    instructions="Fleet-standard demo-app MCP server.",
)

_tauri_desktop = os.environ.get("demo_appTAURI", "").lower() in ("1", "true", "yes")


@mcp.tool()
async def app_info(ctx: Context = None) -> dict:
    """Return metadata about this server.

    ## Return Format
    {"success": bool, "name": str, "version": str, "tool_count": int}

    ## Examples
    app_info()
    """
    tools = await mcp.list_tools()
    return {
        "success": True,
        "name": "demo-app",
        "version": "0.1.0",
        "tool_count": len(tools),
    }


@mcp.tool()
async def example_op(
    operation: str = "hello",
    name: str = "world",
    ctx: Context = None,
) -> dict:
    """Example portmanteau tool - demonstrates the fleet operation pattern.

    ## Return Format
    {"success": bool, "message": str, "data": dict}

    ## Examples
    example_op(operation="hello", name="Sandra")
    example_op(operation="echo", name="ping")
    """
    if operation == "hello":
        return {"success": True, "message": f"Hello, {name}!", "data": {"name": name}}
    if operation == "echo":
        return {"success": True, "message": name, "data": {"echo": name}}
    return {"success": False, "error": f"Unknown operation: {operation}"}


@mcp.resource("skill://demo_app/SKILL.md")
def get_skill() -> str:
    """Expose the bundled skill as an MCP resource."""
    from pathlib import Path

    skill_path = Path(__file__).parent / "skills" / "demo_app" / "SKILL.md"
    return skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""


# ---------------------------------------------------------------------------
# FastAPI app (webapp backend + CORS + health endpoints)
# ---------------------------------------------------------------------------
_mcp_http = mcp.http_app(path="/")
app = FastAPI(title="demo-app", version="0.1.0", lifespan=_mcp_http.lifespan)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    tools = await mcp.list_tools()
    return {
        "status": "ok",
        "server": "demo-app",
        "version": "0.1.0",
        "uptime_seconds": 0,
        "tool_count": len(tools),
    }


@app.get("/api/v1/diagnostics")
async def diagnostics() -> dict[str, Any]:
    tools = await mcp.list_tools()
    return {
        "status": "ok",
        "server": "demo-app",
        "version": "0.1.0",
        "uptime_seconds": 0,
        "tool_count": len(tools),
        "tools": [{"name": t.name} for t in tools],
        "system": {"windows": os.name == "nt"},
        "errors": [],
    }


@app.get("/api/tools")
async def api_tools() -> dict[str, Any]:
    tools = await mcp.list_tools()
    return {
        "success": True,
        "tools": [
            {
                "name": t.name,
                "description": (t.description or "").splitlines()[0],
            }
            for t in tools
        ],
    }


@app.get("/api/skills")
async def api_skills() -> dict[str, Any]:
    return {"success": True, "skills": ["demo_app"]}


@app.get("/skill/{skill_name}")
async def get_skill(skill_name: str) -> str:
    """Return the raw SKILL.md content for a skill name."""
    from pathlib import Path

    skill_path = Path(__file__).parent / "skills" / skill_name / "SKILL.md"
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return "not found"


# ---------------------------------------------------------------------------
# In-memory log ring buffer (fleet UiLog pattern)
# ---------------------------------------------------------------------------
from collections import deque

_LOG_RING: deque[dict] = deque(maxlen=200)


def ring_log(source: str, level: str, message: str) -> None:
    _LOG_RING.appendleft(
        {"ts": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
         "source": source, "level": level, "message": message}
    )


@app.get("/api/logs")
async def api_logs(limit: int = 50) -> dict[str, Any]:
    return {"success": True, "entries": list(_LOG_RING)[:limit], "count": min(limit, len(_LOG_RING))}


# ---------------------------------------------------------------------------
# Membership roster (SQLite)
# ---------------------------------------------------------------------------
@app.get("/api/members")
async def api_members() -> dict[str, Any]:
    members = _db.list_members()
    return {"success": True, "members": members, "count": len(members)}


@app.post("/api/members")
async def api_members_add(payload: dict[str, Any]) -> dict[str, Any]:
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    if not name or not email:
        return {"success": False, "error": "name and email required"}
    try:
        member = _db.add_member(name, email, (payload.get("role") or "member").strip())
    except Exception as exc:
        return {"success": False, "error": str(exc)}
    ring_log("roster", "INFO", f"member added: {name} <{email}>")
    return {"success": True, "member": member}


@app.delete("/api/members/{member_id}")
async def api_members_delete(member_id: int) -> dict[str, Any]:
    ok = _db.delete_member(member_id)
    if ok:
        ring_log("roster", "INFO", f"member removed: id {member_id}")
    return {"success": ok, "id": member_id}


# ---------------------------------------------------------------------------
# Webshop (products + orders, SQLite)
# ---------------------------------------------------------------------------
@app.get("/api/products")
async def api_products() -> dict[str, Any]:
    return {"success": True, "products": _db.list_products()}


@app.post("/api/orders")
async def api_orders_create(payload: dict[str, Any]) -> dict[str, Any]:
    items = payload.get("items")
    total = payload.get("total_cents")
    if not isinstance(items, str) or not isinstance(total, int):
        return {"success": False, "error": "items (str) and total_cents (int) required"}
    order = _db.create_order(items, total)
    ring_log("shop", "INFO", f"order {order['id']} placed for {total / 100:.2f} EUR")
    return {"success": True, "order": order}


# ---------------------------------------------------------------------------
# Scheduler (APScheduler periodic jobs) - the robot patrol foundation
# ---------------------------------------------------------------------------
if os.environ.get("ENABLE_SCHEDULER", "1") == "1":
    from apscheduler.schedulers.background import BackgroundScheduler

    _JOBS: dict[str, dict] = {}
    _scheduler = BackgroundScheduler()


    def _patrol_tick() -> None:
        _JOBS["patrol"] = {
            "name": "patrol",
            "last_run": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
            "status": "ok",
            "message": "periodic safety patrol completed",
        }
        ring_log("scheduler", "INFO", "patrol tick")


    _scheduler.add_job(_patrol_tick, "interval", minutes=5, id="patrol")
    _scheduler.start()
    ring_log("scheduler", "INFO", "scheduler started")


    @app.get("/api/jobs")
    async def api_jobs() -> dict[str, Any]:
        jobs = [
            {"id": j.id, "next_run": str(j.next_run_time or ""), "enabled": not j.next_run_time is None}
            for j in _scheduler.get_jobs()
        ]
        return {"success": True, "jobs": jobs, "runs": _JOBS}


    @app.post("/api/jobs/{job_id}/run")
    async def run_job(job_id: str) -> dict[str, Any]:
        if job_id == "patrol":
            _patrol_tick()
            return {"success": True, "message": "patrol dispatched"}
        return {"success": False, "error": f"unknown job: {job_id}"}


    @app.on_event("shutdown")
    async def _stop_scheduler() -> None:
        _scheduler.shutdown(wait=False)


# ---------------------------------------------------------------------------
# Optional feature endpoints
# ---------------------------------------------------------------------------
if os.environ.get("ENABLE_UPLOAD", "0") == "1":
    from pathlib import Path

    _UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "data/uploads"))
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    @app.post("/api/upload")
    async def upload(file: Any = None) -> dict[str, Any]:
        return {"success": False, "error": "multipart body expected"}

if os.environ.get("ENABLE_EMAIL", "0") == "1":
    @app.post("/api/contact")
    async def contact(subject: str = "", body: str = "") -> dict[str, Any]:
        if not subject or not body:
            return {"success": False, "error": "subject and body required"}
        return {"success": True, "message": "email queued (configure SMTP in .env)"}

if os.environ.get("ENABLE_REALTIME", "0") == "1":
    from fastapi import WebSocket

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_text(f"echo: {data}")
        except Exception:
            pass


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{os.environ.get('WEB_PORT', '11141')}",
        f"http://127.0.0.1:{os.environ.get('WEB_PORT', '11141')}",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=(
        r"https?://(?:[a-zA-Z0-9-]+\.ts\.net|.*?\.tail-[a-f0-9]+\.ts\.net|"
        r"tauri\.localhost|localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|"
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|100\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?$"
        r"|^tauri://localhost$"
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/mcp", _mcp_http)


def main() -> None:
    import uvicorn

    port = int(os.environ.get("WEB_PORT", "11140"))
    host = os.environ.get("WEB_HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()