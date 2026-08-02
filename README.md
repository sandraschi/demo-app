# demo-app

SOTA demo fullstack app - fleet MCP hookups, scheduler, robot patrols, roster, shop

Fleet-standard fullstack app: FastMCP 3.4 backend, React + Vite + Tailwind frontend, Bun, optional Tauri 2.0 desktop wrapper.

## Quick start

```powershell
uv sync
bun --prefix webapp install
.\start.ps1          # clears ports, starts backend + frontend, opens browser
```

- Backend API + Swagger: http://127.0.0.1:11140/docs
- Frontend: http://127.0.0.1:11141
- MCP endpoint (when enabled): http://127.0.0.1:11140/mcp

## Tests

```powershell
uv run pytest tests/        # backend
bun --prefix webapp run e2e # Playwright
```

## Ports

Registered in the fleet reservoir: backend 11140, frontend 11141 (see `mcp-central-docs/operations/WEBAPP_PORTS.md`).