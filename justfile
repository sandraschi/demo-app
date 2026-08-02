# demo-app - fleet justfile
serve port="11140":
    uv run uvicorn demo_app.server:app --host 127.0.0.1 --port {{port}}

mcp-stdio:
    uv run demo_app-server

dev:
    pwsh -NoProfile -File start.ps1

lint:
    uv run ruff check .
    uv run ruff format . --check

fix:
    uv run ruff check . --fix
    uv run ruff format .

test:
    uv run pytest tests/ -q

e2e:
    Set-Location webapp
    npx playwright test

bootstrap:
    uv sync
    Set-Location webapp
    bun install